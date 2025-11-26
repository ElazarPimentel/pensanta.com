#!/usr/bin/env python3
# file:aiql.py
# version 5.3
#
# AIQL - AI-Assisted SQL Editor
# Created by: elazar.pimentel@pensanta.com
# Website: https://elazarpimentel.com/en/tools/aiql
# GitHub: https://github.com/ElazarPimentel/aiql
#
# ============================================================================
# PURPOSE:
# ============================================================================
# AIQL is a FREE collaborative database interface that bridges human users
# and AI assistants (like Claude Code) to work with databases together.
#
# ============================================================================
# HOW IT WORKS (The Collaboration Loop):
# ============================================================================
# 1. User selects a database profile (PostgreSQL, MySQL, MariaDB, or API)
# 2. AIQL writes profile details to aiql.json in the working directory
# 3. Top tabs show input.sql (queries) and output.txt (results)
# 4. Bottom terminal runs Claude Code (the AI assistant)
# 5. AI reads aiql.json to know which files to work with
# 6. User asks AI: "show me all tables in database"
# 7. AI writes SQL to the input.sql file
# 8. User reviews the query and clicks "Run SQL" (F5 or Ctrl+R)
# 9. AIQL executes the query and writes results to output.txt
# 10. Both user and AI read the results from output.txt
# 11. User and AI discuss results and iterate
#
# ============================================================================
# THE WORKFLOW:
# ============================================================================
# User talks to AI → AI writes SQL to input file → User runs query →
# Both see results in output file → Discuss and repeat
#
# This eliminates window switching and provides a free AI-powered database
# exploration tool without expensive subscriptions.
#
# ============================================================================
# DATA STORAGE (Privacy & Security):
# ============================================================================
# AIQL stores configuration in ~/.aiql/ directory:
# - profiles.json: Database connection profiles (includes passwords - keep safe!)
# - history.db: SQLite database with file/command history (NO passwords)
# - active.json: Currently active profile metadata
#
# In your working directory:
# - aiql.json: Current profile metadata (no passwords, safe to commit)
#
# SECURITY NOTES:
# - Passwords are stored in plaintext in profiles.json (in your home directory)
# - Never commit profiles.json to git (use .gitignore)
# - Use api-remote mode for production databases when possible
# - Always review SQL queries before executing them
#
# ============================================================================
# CLAUDE CODE INTEGRATION:
# ============================================================================
# This application is designed specifically for use with Claude Code AI.
# Run Claude Code in the bottom terminal and it will:
# - Automatically read aiql.json to understand your database setup
# - Write SQL queries to your input file when you ask questions
# - Read query results from your output file to discuss with you
# - Help you explore, analyze, and manage your databases conversationally

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, GtkSource, Vte, GLib, Gdk, Gio
import os
import sqlite3
import json
from pathlib import Path
import time
import subprocess
import re
from datetime import datetime
import threading

class NotificationWindow(Gtk.Window):
    """
    Floating notification window that blinks red when SQL output is ready

    A small (128x128) window that stays on top and can be moved around.
    When triggered, it blinks red 4 times to alert the user.
    """

    def __init__(self):
        super().__init__()

        # Window properties
        self.set_default_size(128, 128)
        self.set_decorated(True)  # Show title bar so it can be moved
        self.set_title("AIQL Alert")
        self.set_keep_above(True)  # Always on top
        self.set_skip_taskbar_hint(True)  # Don't show in taskbar
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)  # Floating utility window

        # Create drawing area for custom colors
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)

        # Current color state
        self.is_red = False
        self.blink_count = 0
        self.blink_timeout_id = None

        # Set black background initially
        self.set_color_black()

    def on_draw(self, widget, cr):
        """Draw the colored rectangle"""
        # Get the allocated size
        allocation = widget.get_allocation()
        width = allocation.width
        height = allocation.height

        # Set color based on state
        if self.is_red:
            cr.set_source_rgb(1.0, 0.0, 0.0)  # Red
        else:
            cr.set_source_rgb(0.0, 0.0, 0.0)  # Black

        # Fill the entire area
        cr.rectangle(0, 0, width, height)
        cr.fill()

        return False

    def set_color_black(self):
        """Set window to black"""
        self.is_red = False
        self.drawing_area.queue_draw()

    def set_color_red(self):
        """Set window to red"""
        self.is_red = True
        self.drawing_area.queue_draw()

    def blink_red(self, times=4):
        """
        Blink red the specified number of times

        Each blink is 250ms on, 250ms off (500ms total per blink)
        """
        # Cancel any ongoing blink
        if self.blink_timeout_id:
            GLib.source_remove(self.blink_timeout_id)

        # Reset state
        self.blink_count = 0
        self.set_color_black()

        # Start blinking
        def blink_step():
            if self.blink_count >= times * 2:  # Each blink is 2 steps (on + off)
                # Done blinking, stay black
                self.set_color_black()
                self.blink_timeout_id = None
                return False

            # Toggle color
            if self.blink_count % 2 == 0:
                self.set_color_red()
            else:
                self.set_color_black()

            self.blink_count += 1
            return True  # Continue blinking

        # Blink every 250ms
        self.blink_timeout_id = GLib.timeout_add(250, blink_step)

class AIQLApp(Gtk.Window):
    """
    Main AIQL Application Window

    This GTK3 application provides a split-pane interface with:
    - Top: Two editor tabs for SQL input and results output
    - Bottom: Terminal for running Claude Code AI assistant
    - Controls: Profile selector and Run SQL button

    The app manages database connection profiles and facilitates collaboration
    between the user and Claude Code AI through shared files (aiql.json).
    """

    # UI Layout Constants
    EDITOR_SPLIT_RATIO = 0.6  # 60% screen height for editors, 40% for terminal
    UNDO_LEVELS = 100         # Number of undo steps in text editors
    AUTOSAVE_DELAY_MS = 500   # Milliseconds to wait before auto-saving (currently disabled)
    MAX_RECENT_FILES = 5      # Maximum recent files to remember in history

    def __init__(self):
        """Initialize the main AIQL window and set up all components"""
        super().__init__()
        self.set_default_size(1200, 800)
        self.connect("destroy", self.on_quit)

        # Set window icon
        try:
            self.set_icon_name("applications-database")
        except:
            pass

        # Force dark theme before building UI
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        # Create HeaderBar for dark theme title bar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title("AIQL - SQL Editor v5.3")
        self.set_titlebar(headerbar)
        
        # Initialize paths
        self.config_dir = Path.home() / ".aiql"
        self.config_dir.mkdir(exist_ok=True)
        self.db_path = self.config_dir / "history.db"
        self.profiles_path = self.config_dir / "profiles.json"
        self.active_json_path = self.config_dir / "active.json"
        self.init_database()
        
        # Use aiql.py's directory as base for relative paths
        self.cwd = Path(__file__).parent.resolve()
        
        # Connection profiles
        self.profiles = self.load_profiles()
        self.current_profile = None
        
        # File paths for tabs
        self.tab1_file = None
        self.tab2_file = None
        
        # File monitors
        self.tab1_monitor = None
        self.tab2_monitor = None
        
        # Auto-save timeout IDs
        self.tab1_save_timeout = None
        self.tab2_save_timeout = None
        
        # Tab02 reload debounce and saving state
        self.tab2_pending_reload_id = None
        self.tab2_is_saving = False
        
        # Dark theme flag (start with dark theme enabled)
        self.dark_theme = True

        # Beep on output flag (start enabled)
        self.beep_on_output = True

        # Shared CSS provider for editors
        self.editor_css_provider = None

        # Run SQL button reference and CSS provider
        self.run_sql_btn = None
        self.run_sql_btn_css_provider = None

        # Create floating notification window
        self.notification_window = NotificationWindow()
        self.notification_window.show_all()

        # Build UI
        self.build_ui()

        # Load last opened files
        self.load_recent_files()
        
    def init_database(self):
        """
        Initialize SQLite database for history tracking

        Creates history.db in ~/.aiql/ directory with two tables:

        1. recent_files: Tracks recently opened files in tabs
           - Stores: file paths, working directories, timestamps
           - Used for: Quick file access, session restoration

        2. terminal_history: Tracks commands executed in terminals
           - Stores: commands, working directories, timestamps
           - Used for: Command history navigation

        SECURITY: This database does NOT store passwords or credentials.
        It only stores file paths and command history for convenience.
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Recent files table - stores which files were opened in which tabs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS recent_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tab_number INTEGER NOT NULL,        -- Which tab (1 or 2)
                        file_path TEXT NOT NULL,            -- Full path to file
                        working_dir TEXT NOT NULL,          -- Directory context
                        last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Terminal history table - stores command history for terminals
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS terminal_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        terminal_number INTEGER NOT NULL,   -- Which terminal
                        working_dir TEXT NOT NULL,          -- Where command was run
                        command TEXT NOT NULL,              -- The actual command
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        
    def build_ui(self):
        """Build the main UI layout"""
        # Main vertical box
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_vbox)
        
        # Menu bar
        menubar = self.create_menubar()
        main_vbox.pack_start(menubar, False, False, 0)
        
        # Main paned (vertical split: editor area / terminal area)
        self.main_paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        main_vbox.pack_start(self.main_paned, True, True, 0)
        
        # Top: Notebook for tabs (editor area)
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        
        # Tab 1: input.sql
        self.tab1_view = self.create_source_view()
        self.tab1_view.connect("key-press-event", self.on_editor_key_press)
        self.tab1_scroll = Gtk.ScrolledWindow()
        self.tab1_scroll.add(self.tab1_view)
        self.notebook.append_page(self.tab1_scroll, Gtk.Label(label="Tab01: input.sql"))

        # Tab 2: output.txt
        self.tab2_view = self.create_source_view()
        self.tab2_view.connect("key-press-event", self.on_editor_key_press)
        self.tab2_scroll = Gtk.ScrolledWindow()
        self.tab2_scroll.add(self.tab2_view)
        self.notebook.append_page(self.tab2_scroll, Gtk.Label(label="Tab02: output.txt"))
        
        self.main_paned.pack1(self.notebook, resize=True, shrink=False)

        # ========================================================================
        # Bottom: Claude Code Terminal
        # This terminal is where the user runs Claude Code AI to collaborate
        # on database work. Claude Code reads aiql.json to know which files
        # to use for SQL input/output.
        # ========================================================================
        term2_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        term2_label = Gtk.Label(label="Claude Code Terminal")
        term2_label.set_xalign(0)
        term2_vbox.pack_start(term2_label, False, False, 2)

        # Button row: [Generate CC Guide] [Profile Dropdown] [Manage] ... [Run SQL →]
        term2_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        term2_button_box.set_margin_start(5)
        term2_button_box.set_margin_end(5)
        term2_button_box.set_margin_top(2)
        term2_button_box.set_margin_bottom(2)

        # Generate CC Guide button (left side)
        gen_guide_btn = Gtk.Button(label="Generate CC Guide")
        gen_guide_btn.connect("clicked", self.on_generate_cc_guide_clicked)
        term2_button_box.pack_start(gen_guide_btn, False, False, 0)

        # Profile selector dropdown (fixed width ~30-40 chars)
        self.profile_combo = Gtk.ComboBoxText()
        self.profile_combo.set_entry_text_column(0)
        self.profile_combo.set_size_request(350, -1)  # ~40 chars width
        self.profile_combo.connect("changed", self.on_profile_changed)
        self.refresh_profile_combo()
        term2_button_box.pack_start(self.profile_combo, False, False, 0)

        # Manage profiles button (next to dropdown)
        manage_btn = Gtk.Button(label="Manage")
        manage_btn.connect("clicked", self.on_manage_profiles_clicked)
        term2_button_box.pack_start(manage_btn, False, False, 0)

        # Run SQL button (right of Manage button)
        self.run_sql_btn = Gtk.Button(label="Run SQL")
        self.run_sql_btn.connect("clicked", self.on_run_sql_clicked)
        term2_button_box.pack_start(self.run_sql_btn, False, False, 0)

        # Initialize button to green (ready) state
        self.set_run_sql_button_state('green')

        # Beep checkbox (right of Run SQL button, enabled by default)
        self.beep_checkbox = Gtk.CheckButton(label="Beep")
        self.beep_checkbox.set_active(True)
        self.beep_checkbox.connect("toggled", self.on_beep_toggled)
        term2_button_box.pack_start(self.beep_checkbox, False, False, 5)

        term2_vbox.pack_start(term2_button_box, False, False, 0)
        
        self.terminal2 = Vte.Terminal()
        self.setup_terminal(self.terminal2, 2)
        term2_scroll = Gtk.ScrolledWindow()
        term2_scroll.add(self.terminal2)
        term2_vbox.pack_start(term2_scroll, True, True, 0)

        self.main_paned.pack2(term2_vbox, resize=False, shrink=False)
        
        # Set initial pane positions (60/40 split)
        GLib.idle_add(self.set_initial_pane_positions)

        # Auto-save disabled - manual save only via Ctrl+S
        # self.tab1_view.get_buffer().connect("changed", self.on_tab1_changed)
        
    def set_initial_pane_positions(self):
        """Set initial pane positions after window is realized"""
        height = self.get_allocated_height()
        self.main_paned.set_position(int(height * self.EDITOR_SPLIT_RATIO))
        return False
        
    def create_menubar(self):
        """Create application menu bar"""
        menubar = Gtk.MenuBar()
        
        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        
        open_tab1 = Gtk.MenuItem(label="Open in Tab01...")
        open_tab1.connect("activate", self.on_open_tab1)
        file_menu.append(open_tab1)
        
        open_tab2 = Gtk.MenuItem(label="Open in Tab02...")
        open_tab2.connect("activate", self.on_open_tab2)
        file_menu.append(open_tab2)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        recent_tab1 = Gtk.MenuItem(label="Recent Files (Tab01)")
        recent_tab1.connect("activate", self.show_recent_tab1)
        file_menu.append(recent_tab1)
        
        recent_tab2 = Gtk.MenuItem(label="Recent Files (Tab02)")
        recent_tab2.connect("activate", self.show_recent_tab2)
        file_menu.append(recent_tab2)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        file_menu.append(quit_item)
        
        menubar.append(file_item)
        
        # View menu
        view_menu = Gtk.Menu()
        view_item = Gtk.MenuItem(label="View")
        view_item.set_submenu(view_menu)

        dark_theme = Gtk.CheckMenuItem(label="Dark Theme")
        dark_theme.set_active(True)  # Start checked since dark theme is enabled
        dark_theme.connect("toggled", self.toggle_dark_theme)
        view_menu.append(dark_theme)

        menubar.append(view_item)

        # Help menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)

        data_storage_item = Gtk.MenuItem(label="Data Storage Info")
        data_storage_item.connect("activate", self.show_data_storage_info)
        help_menu.append(data_storage_item)

        help_menu.append(Gtk.SeparatorMenuItem())

        about_item = Gtk.MenuItem(label="About AIQL")
        about_item.connect("activate", self.show_about_dialog)
        help_menu.append(about_item)

        menubar.append(help_item)

        return menubar
        
    def create_source_view(self):
        """Create a GtkSourceView widget with SQL highlighting"""
        view = GtkSource.View()
        view.set_show_line_numbers(True)
        view.set_auto_indent(True)
        view.set_indent_width(4)
        view.set_insert_spaces_instead_of_tabs(True)
        view.set_highlight_current_line(True)
        view.set_show_right_margin(False)
        view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)  # Enable word wrap
        
        # Enable undo/redo
        buffer = view.get_buffer()
        buffer.set_max_undo_levels(self.UNDO_LEVELS)
        
        # Set SQL syntax highlighting
        lang_manager = GtkSource.LanguageManager()
        sql_lang = lang_manager.get_language('sql')
        if sql_lang:
            buffer.set_language(sql_lang)
            
        # Set style scheme (will be updated by theme toggle)
        self.apply_editor_theme(buffer)
        
        # Force dark background colors (create CSS provider once)
        if not self.editor_css_provider:
            self.editor_css_provider = Gtk.CssProvider()
            self.editor_css_provider.load_from_data(b"""
                textview {
                    background-color: #2e3436;
                    color: #d3d7cf;
                }
                textview text {
                    background-color: #2e3436;
                    color: #d3d7cf;
                }
            """)
        
        context = view.get_style_context()
        context.add_provider(self.editor_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
        return view
        
    def apply_editor_theme(self, buffer):
        """Apply current theme to editor buffer"""
        style_manager = GtkSource.StyleSchemeManager()
        scheme_name = 'oblivion' if self.dark_theme else 'classic'
        scheme = style_manager.get_scheme(scheme_name)
        if scheme:
            buffer.set_style_scheme(scheme)

    def set_run_sql_button_state(self, state):
        """
        Set Run SQL button visual state

        States:
        - 'green': Ready (initial, after Tab01 changes)
        - 'yellow': Executing SQL
        - 'red': Results ready (success)
        - 'pink': Error occurred
        """
        if not self.run_sql_btn:
            return

        # Remove old CSS provider if exists
        if self.run_sql_btn_css_provider:
            context = self.run_sql_btn.get_style_context()
            context.remove_provider(self.run_sql_btn_css_provider)

        # Define CSS for each state
        css_templates = {
            'green': b"""
                button {
                    color: #00ff00;
                    border: 2px solid #00ff00;
                    font-weight: bold;
                }
                button:hover {
                    background: #003300;
                }
            """,
            'yellow': b"""
                button {
                    color: #ffff00;
                    border: 2px solid #ffff00;
                    background: #333300;
                    font-weight: bold;
                }
                button:hover {
                    background: #444400;
                }
            """,
            'red': b"""
                button {
                    color: #ff0000;
                    border: 2px solid #ff0000;
                    background: #330000;
                    font-weight: bold;
                }
                button:hover {
                    background: #440000;
                }
            """,
            'pink': b"""
                button {
                    color: #ff69b4;
                    border: 2px solid #ff69b4;
                    background: #330022;
                    font-weight: bold;
                }
                button:hover {
                    background: #440033;
                }
            """
        }

        # Apply new CSS
        if state in css_templates:
            self.run_sql_btn_css_provider = Gtk.CssProvider()
            self.run_sql_btn_css_provider.load_from_data(css_templates[state])
            context = self.run_sql_btn.get_style_context()
            context.add_provider(self.run_sql_btn_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
    def setup_terminal(self, terminal, term_number):
        """Setup VTE terminal with bash shell"""
        # Enable focus for proper key handling (ESC, etc.)
        terminal.set_can_focus(True)

        # Enable mouse events and cursor shape
        terminal.set_mouse_autohide(True)
        terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)

        # Connect right-click for context menu
        terminal.connect("button-press-event", self.on_terminal_button_press)

        # Connect key press for Ctrl+Shift+V/C
        terminal.connect("key-press-event", self.on_terminal_key_press)

        # Get the directory where this script is running
        script_dir = os.path.dirname(os.path.abspath(__file__))

        terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            script_dir,  # Use script directory as working directory
            ['/bin/bash'],
            [],
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            -1,
            None,
            None
        )
        
    def on_terminal_button_press(self, terminal, event):
        """Handle right-click on terminal for context menu"""
        if event.button == 3:  # Right-click
            menu = Gtk.Menu()

            # Copy menu item
            copy_item = Gtk.MenuItem(label="Copy")
            copy_item.connect("activate", lambda w: terminal.copy_clipboard())
            menu.append(copy_item)

            # Paste menu item
            paste_item = Gtk.MenuItem(label="Paste")
            paste_item.connect("activate", lambda w: terminal.paste_clipboard())
            menu.append(paste_item)

            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)
            return True
        return False

    def on_terminal_key_press(self, terminal, event):
        """Handle Ctrl+Shift+C/V for copy/paste in terminal"""
        # Check for Ctrl+Shift
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.state & Gdk.ModifierType.SHIFT_MASK:
            # Ctrl+Shift+C - Copy
            if event.keyval == Gdk.KEY_C:
                terminal.copy_clipboard()
                return True
            # Ctrl+Shift+V - Paste
            elif event.keyval == Gdk.KEY_V:
                terminal.paste_clipboard()
                return True
        return False

    def on_editor_key_press(self, view, event):
        """Handle keyboard shortcuts in editors"""
        # Ctrl+S - Save current tab
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_s:
            current_page = self.notebook.get_current_page()
            if current_page == 0:
                self.save_tab1()
            elif current_page == 1:
                self.save_tab2()
            return True

        # F5 - Run SQL
        if event.keyval == Gdk.KEY_F5:
            self.on_run_sql_clicked(None)
            return True

        # Ctrl+R - Run SQL
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_r:
            self.on_run_sql_clicked(None)
            return True

        return False

    def load_profiles(self):
        """Load connection profiles from JSON file"""
        if self.profiles_path.exists():
            try:
                with open(self.profiles_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
        return {}

    def save_profiles(self):
        """Save connection profiles to JSON file"""
        try:
            with open(self.profiles_path, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")

    def path_with_tilde(self, filepath):
        """Convert absolute path to use ~ notation if in home directory"""
        if not filepath:
            return filepath

        try:
            path = Path(filepath).resolve()
            home = Path.home()

            # Check if path starts with home directory
            try:
                rel_path = path.relative_to(home)
                return str(Path('~') / rel_path)
            except ValueError:
                # Path is not relative to home
                return str(path)
        except Exception:
            return filepath

    def update_active_json(self):
        """Update active.json with currently loaded files"""
        try:
            active_data = {
                "tab1_file": self.path_with_tilde(self.tab1_file),
                "tab2_file": self.path_with_tilde(self.tab2_file),
                "current_profile": self.current_profile,
                "working_directory": self.path_with_tilde(str(self.cwd)),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(self.active_json_path, 'w') as f:
                json.dump(active_data, f, indent=2)
        except Exception as e:
            print(f"Error updating active.json: {e}")

    def write_aiql_json(self, profile_name, profile):
        """
        Write aiql.json to current working directory - THE HANDSHAKE FILE

        This is the critical "handshake" file that tells Claude Code AI:
        - Which SQL input file to write queries to (sourceFile)
        - Which output file to read results from (outputFile)
        - What database it's working with (dbType, databaseName, host)

        IMPORTANT FOR CLAUDE CODE:
        When you (Claude Code) see an aiql.json file, you should:
        1. Read it to understand the current database setup
        2. Write SQL queries to the sourceFile path
        3. Wait for user to click "Run SQL" (F5)
        4. Read results from the outputFile path
        5. Discuss results with the user

        SECURITY NOTE: This file does NOT contain passwords (safe to commit to git)
        """
        try:
            aiql_json_path = Path(self.cwd) / "aiql.json"

            if profile_name and profile:
                # Get file paths from profile
                source_file = profile.get('source_file', '')
                output_file = profile.get('output_file', '')

                # Resolve relative paths to absolute paths first
                if source_file and not Path(source_file).is_absolute():
                    source_file = str(Path(self.cwd) / source_file)
                if output_file and not Path(output_file).is_absolute():
                    output_file = str(Path(self.cwd) / output_file)

                # Build the handshake data structure
                aiql_data = {
                    "profileName": profile_name,                           # Human-readable profile name
                    "sourceFile": self.path_with_tilde(source_file),      # Where Claude Code writes SQL
                    "outputFile": self.path_with_tilde(output_file),      # Where Claude Code reads results
                    "dbType": profile.get('db_type', ''),                 # postgresql/mysql/mariadb/api-remote
                    "databaseName": profile.get('database', ''),          # Database name
                    "host": profile.get('host', ''),                      # Host (or API URL for api-remote)
                    "port": profile.get('port', ''),                      # Port number
                    "username": profile.get('username', ''),              # Database username (NO password!)
                    "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                # No profile selected - write empty/null state
                aiql_data = {
                    "profileName": None,
                    "sourceFile": None,
                    "outputFile": None,
                    "dbType": None,
                    "databaseName": None,
                    "host": None,
                    "port": None,
                    "username": None,
                    "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

            # Write the handshake file
            with open(aiql_json_path, 'w') as f:
                json.dump(aiql_data, f, indent=2)

            print(f"Updated aiql.json with profile: {profile_name or '(No Profile)'}")
        except Exception as e:
            print(f"Error writing aiql.json: {e}")

    def refresh_profile_combo(self):
        """Refresh the profile dropdown list"""
        self.profile_combo.remove_all()
        self.profile_combo.append_text("(No Profile)")
        for profile_name in sorted(self.profiles.keys()):
            self.profile_combo.append_text(profile_name)
        if self.current_profile and self.current_profile in self.profiles:
            self.profile_combo.set_active_id(self.current_profile)
        else:
            self.profile_combo.set_active(0)

    def on_profile_changed(self, combo):
        """Handle profile selection change"""
        profile_name = combo.get_active_text()
        if profile_name and profile_name != "(No Profile)":
            self.current_profile = profile_name
            profile = self.profiles.get(profile_name, {})

            # Handle source file (Tab 1)
            if profile.get('source_file'):
                source_path = Path(profile['source_file'])
                # Resolve relative paths relative to cwd
                if not source_path.is_absolute():
                    source_path = Path(self.cwd) / source_path
                if not source_path.exists():
                    try:
                        source_path.parent.mkdir(parents=True, exist_ok=True)
                        source_path.write_text("-- SQL queries\n", encoding='utf-8')
                        print(f"Created source file: {source_path}")
                    except Exception as e:
                        print(f"Error creating source file: {e}")
                self.load_file_to_tab1(str(source_path))

            # Handle output file (Tab 2)
            if profile.get('output_file'):
                output_path = Path(profile['output_file'])
                # Resolve relative paths relative to cwd
                if not output_path.is_absolute():
                    output_path = Path(self.cwd) / output_path
                if not output_path.exists():
                    try:
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        output_path.write_text("", encoding='utf-8')
                        print(f"Created output file: {output_path}")
                    except Exception as e:
                        print(f"Error creating output file: {e}")
                self.load_file_to_tab2(str(output_path))

            # Write aiql.json with current profile details
            self.write_aiql_json(profile_name, profile)

            # Update active.json after loading profile files
            self.update_active_json()
        else:
            self.current_profile = None
            self.write_aiql_json(None, None)
            self.update_active_json()

    def on_manage_profiles_clicked(self, widget):
        """Show profile management dialog"""
        dialog = Gtk.Dialog(
            title="Manage Connection Profiles",
            parent=self,
            flags=0
        )
        dialog.set_default_size(600, 400)
        dialog.add_buttons(
            "Close", Gtk.ResponseType.CLOSE
        )

        box = dialog.get_content_area()
        
        # List of profiles
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        for profile_name in sorted(self.profiles.keys()):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_margin_start(5)
            hbox.set_margin_end(5)
            label = Gtk.Label(label=profile_name)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            
            edit_btn = Gtk.Button(label="Edit")
            edit_btn.connect("clicked", lambda w, pn=profile_name: self.edit_profile(pn, dialog))
            hbox.pack_start(edit_btn, False, False, 0)

            duplicate_btn = Gtk.Button(label="Duplicate")
            duplicate_btn.connect("clicked", lambda w, pn=profile_name: self.duplicate_profile(pn, dialog))
            hbox.pack_start(duplicate_btn, False, False, 0)

            delete_btn = Gtk.Button(label="Delete")
            delete_btn.connect("clicked", lambda w, pn=profile_name: self.delete_profile(pn, dialog))
            hbox.pack_start(delete_btn, False, False, 0)
            
            row.add(hbox)
            listbox.add(row)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(250)
        scroll.add(listbox)
        box.pack_start(scroll, True, True, 10)
        
        # Add new profile button
        add_btn = Gtk.Button(label="Add New Profile")
        add_btn.connect("clicked", lambda w: self.edit_profile(None, dialog))
        box.pack_start(add_btn, False, False, 5)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def edit_profile(self, profile_name, parent_dialog):
        """Show edit/add profile dialog"""
        is_new = profile_name is None
        profile = self.profiles.get(profile_name, {}) if not is_new else {}
        
        dialog = Gtk.Dialog(
            title="Add Profile" if is_new else f"Edit Profile: {profile_name}",
            parent=parent_dialog or self,
            flags=Gtk.DialogFlags.MODAL
        )
        dialog.set_default_size(500, 600)
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Save", Gtk.ResponseType.OK
        )
        
        box = dialog.get_content_area()
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        # Profile Name
        grid.attach(Gtk.Label(label="Profile Name:", xalign=1), 0, 0, 1, 1)
        name_entry = Gtk.Entry()
        name_entry.set_text(profile_name or "")
        name_entry.set_sensitive(is_new)
        grid.attach(name_entry, 1, 0, 1, 1)
        
        # Source File
        grid.attach(Gtk.Label(label="Source File (Tab 1):", xalign=1), 0, 1, 1, 1)
        source_entry = Gtk.Entry()
        source_entry.set_text(profile.get('source_file', ''))
        grid.attach(source_entry, 1, 1, 1, 1)
        
        # Output File
        grid.attach(Gtk.Label(label="Output File (Tab 2):", xalign=1), 0, 2, 1, 1)
        output_entry = Gtk.Entry()
        output_entry.set_text(profile.get('output_file', ''))
        grid.attach(output_entry, 1, 2, 1, 1)
        
        # Database Type
        grid.attach(Gtk.Label(label="Database Type:", xalign=1), 0, 3, 1, 1)
        db_type_combo = Gtk.ComboBoxText()
        db_type_combo.append_text("postgresql")
        db_type_combo.append_text("mysql")
        db_type_combo.append_text("mariadb")
        db_type_combo.append_text("api-remote")
        current_type = profile.get('db_type', 'postgresql')
        if current_type == "postgresql":
            db_type_combo.set_active(0)
        elif current_type == "mysql":
            db_type_combo.set_active(1)
        elif current_type == "mariadb":
            db_type_combo.set_active(2)
        elif current_type == "api-remote":
            db_type_combo.set_active(3)
        grid.attach(db_type_combo, 1, 3, 1, 1)
        
        # Host
        grid.attach(Gtk.Label(label="Host:", xalign=1), 0, 4, 1, 1)
        host_entry = Gtk.Entry()
        host_entry.set_text(profile.get('host', 'localhost'))
        grid.attach(host_entry, 1, 4, 1, 1)
        
        # Port
        grid.attach(Gtk.Label(label="Port:", xalign=1), 0, 5, 1, 1)
        port_entry = Gtk.Entry()
        port_entry.set_text(profile.get('port', '5432'))
        grid.attach(port_entry, 1, 5, 1, 1)
        
        # Database
        grid.attach(Gtk.Label(label="Database:", xalign=1), 0, 6, 1, 1)
        database_entry = Gtk.Entry()
        database_entry.set_text(profile.get('database', ''))
        grid.attach(database_entry, 1, 6, 1, 1)
        
        # Username
        grid.attach(Gtk.Label(label="Username:", xalign=1), 0, 7, 1, 1)
        username_entry = Gtk.Entry()
        username_entry.set_text(profile.get('username', ''))
        grid.attach(username_entry, 1, 7, 1, 1)
        
        # Password
        grid.attach(Gtk.Label(label="Password:", xalign=1), 0, 8, 1, 1)
        password_entry = Gtk.Entry()
        password_entry.set_text(profile.get('password', ''))
        password_entry.set_visibility(False)
        grid.attach(password_entry, 1, 8, 1, 1)

        box.pack_start(grid, True, True, 0)

        # Test Connection button
        test_btn = Gtk.Button(label="Test Connection")
        test_btn.connect("clicked", lambda w: self.test_connection(
            db_type_combo.get_active_text(),
            host_entry.get_text().strip(),
            port_entry.get_text().strip(),
            database_entry.get_text().strip(),
            username_entry.get_text().strip(),
            password_entry.get_text().strip(),
            dialog
        ))
        box.pack_start(test_btn, False, False, 5)

        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_name = name_entry.get_text().strip()
            if not new_name:
                error_dialog = Gtk.MessageDialog(
                    parent=dialog,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Profile name cannot be empty"
                )
                error_dialog.run()
                error_dialog.destroy()
                dialog.destroy()
                return
            
            # Remove old profile if renamed
            if not is_new and new_name != profile_name:
                del self.profiles[profile_name]
            
            self.profiles[new_name] = {
                'source_file': source_entry.get_text().strip(),
                'output_file': output_entry.get_text().strip(),
                'db_type': db_type_combo.get_active_text(),
                'host': host_entry.get_text().strip(),
                'port': port_entry.get_text().strip(),
                'database': database_entry.get_text().strip(),
                'username': username_entry.get_text().strip(),
                'password': password_entry.get_text().strip()
            }
            
            self.save_profiles()
            self.refresh_profile_combo()
            
            if parent_dialog:
                parent_dialog.destroy()
                self.on_manage_profiles_clicked(None)
        
        dialog.destroy()

    def delete_profile(self, profile_name, parent_dialog):
        """Delete a connection profile"""
        confirm = Gtk.MessageDialog(
            parent=parent_dialog,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete profile '{profile_name}'?"
        )
        response = confirm.run()
        confirm.destroy()
        
        if response == Gtk.ResponseType.YES:
            del self.profiles[profile_name]
            self.save_profiles()
            self.refresh_profile_combo()
            if self.current_profile == profile_name:
                self.current_profile = None
            parent_dialog.destroy()
            self.on_manage_profiles_clicked(None)

    def duplicate_profile(self, profile_name, parent_dialog):
        """Duplicate a connection profile with a new name"""
        if profile_name not in self.profiles:
            return

        # Prompt for new profile name
        name_dialog = Gtk.Dialog(
            title=f"Duplicate Profile: {profile_name}",
            parent=parent_dialog,
            flags=Gtk.DialogFlags.MODAL
        )
        name_dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Duplicate", Gtk.ResponseType.OK
        )

        box = name_dialog.get_content_area()
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        label = Gtk.Label(label="New profile name:")
        box.pack_start(label, False, False, 5)

        entry = Gtk.Entry()
        entry.set_text(f"{profile_name}_copy")
        box.pack_start(entry, False, False, 5)

        name_dialog.show_all()
        response = name_dialog.run()

        if response == Gtk.ResponseType.OK:
            new_name = entry.get_text().strip()

            if not new_name:
                error_dialog = Gtk.MessageDialog(
                    parent=name_dialog,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Profile name cannot be empty"
                )
                error_dialog.run()
                error_dialog.destroy()
                name_dialog.destroy()
                return

            if new_name in self.profiles:
                error_dialog = Gtk.MessageDialog(
                    parent=name_dialog,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Profile '{new_name}' already exists"
                )
                error_dialog.run()
                error_dialog.destroy()
                name_dialog.destroy()
                return

            # Copy the profile
            self.profiles[new_name] = self.profiles[profile_name].copy()
            self.save_profiles()
            self.refresh_profile_combo()

            # Refresh the manage profiles dialog
            parent_dialog.destroy()
            self.on_manage_profiles_clicked(None)

        name_dialog.destroy()

    def test_connection(self, db_type, host, port, database, username, password, parent_dialog):
        """Test database connection"""
        if not all([db_type, host, port, database, username]):
            error_dialog = Gtk.MessageDialog(
                parent=parent_dialog,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Please fill in all connection fields"
            )
            error_dialog.run()
            error_dialog.destroy()
            return

        # Build test command based on database type
        if db_type == 'postgresql':
            connection_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            command = ["psql", connection_url, "-c", "SELECT 1;"]
        elif db_type in ['mysql', 'mariadb']:
            command = [
                "mysql",
                f"--host={host}",
                f"--port={port}",
                f"--user={username}",
                f"--password={password}",
                database,
                "-e", "SELECT 1;"
            ]
        else:
            error_dialog = Gtk.MessageDialog(
                parent=parent_dialog,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Unsupported database type: {db_type}"
            )
            error_dialog.run()
            error_dialog.destroy()
            return

        # Test the connection
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                success_dialog = Gtk.MessageDialog(
                    parent=parent_dialog,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Connection successful!"
                )
                success_dialog.format_secondary_text(f"Successfully connected to {database} @ {host}")
                success_dialog.run()
                success_dialog.destroy()
            else:
                error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                error_dialog = Gtk.MessageDialog(
                    parent=parent_dialog,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Connection failed"
                )
                error_dialog.format_secondary_text(error_msg[:500])  # Limit error message length
                error_dialog.run()
                error_dialog.destroy()

        except subprocess.TimeoutExpired:
            error_dialog = Gtk.MessageDialog(
                parent=parent_dialog,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Connection timeout"
            )
            error_dialog.format_secondary_text("Connection attempt took longer than 10 seconds")
            error_dialog.run()
            error_dialog.destroy()
        except Exception as e:
            error_dialog = Gtk.MessageDialog(
                parent=parent_dialog,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Connection error"
            )
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()

    def on_run_sql_clicked(self, widget):
        """
        Execute SQL from profile's source file and write to profile's output file

        Auto-saves Tab 1 before executing to ensure latest SQL is run.
        """
        # Set button to yellow (executing) state
        self.set_run_sql_button_state('yellow')

        if not self.current_profile:
            error_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="No profile selected"
            )
            error_dialog.run()
            error_dialog.destroy()
            return

        profile = self.profiles.get(self.current_profile)
        if not profile:
            return

        # Auto-save Tab 1 before executing (ensures we run the latest SQL)
        if self.tab1_file:
            self.save_tab1()

        # Get source file from profile
        source_file = profile.get('source_file')
        if not source_file:
            error_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="No source file configured in profile"
            )
            error_dialog.run()
            error_dialog.destroy()
            return
        
        source_path = Path(source_file)
        # Resolve relative paths relative to cwd
        if not source_path.is_absolute():
            source_path = Path(self.cwd) / source_path
        if not source_path.exists():
            error_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Source file does not exist: {source_file}"
            )
            error_dialog.run()
            error_dialog.destroy()
            return
        
        # Read SQL content from profile's source file
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            error_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Error reading SQL file: {e}"
            )
            error_dialog.run()
            error_dialog.destroy()
            return
        
        if not sql_content.strip():
            error_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="SQL file is empty"
            )
            error_dialog.run()
            error_dialog.destroy()
            return
        
        # Execute SQL based on database type
        self.execute_sql(sql_content, profile)

    def on_generate_cc_guide_clicked(self, widget):
        """
        Generate cc-aiql-manual.yaml file for Claude Code

        This creates a YAML guide file that explains to Claude Code how to
        use AIQL for database collaboration. When Claude Code reads this file,
        it will understand the workflow and file locations.
        """
        try:
            guide_path = Path(self.cwd) / "cc-aiql-manual.yaml"

            guide_content = """# AIQL - Claude Code Integration Guide
# This file explains how Claude Code should work with AIQL

## What is AIQL?
AIQL is a collaborative database interface that allows you (Claude Code) and
the user to work together on database tasks through shared files.

## The Workflow

### 1. Read the aiql.json file
When you start, read the `aiql.json` file in this directory to understand:
- sourceFile: Where you should write SQL queries
- outputFile: Where you read query results
- dbType: Type of database (postgresql/mysql/mariadb/api-remote)
- databaseName: Which database you're working with
- host: Database server or API endpoint
- username: Database username (NO password in this file)

### 2. When the user asks a database question

Example: "Show me all tables in the database"

You should:
1. Read aiql.json to get the sourceFile path
2. Write appropriate SQL to that file (e.g., `SHOW TABLES;` for MySQL)
3. Tell the user: "SQL query written! Click 'Run SQL' (F5) when ready."
4. Wait for user to execute the query

### 3. After the user runs the query

The user clicks "Run SQL" (F5) in AIQL, which:
1. Reads SQL from sourceFile
2. Executes it against the database
3. Writes results to outputFile

### 4. Read and discuss results

You should:
1. Read the outputFile to see the query results
2. Analyze and discuss the results with the user
3. Answer follow-up questions or suggest next steps

### 5. Iterate

Continue this loop:
- User asks question → You write SQL → User runs it → You read results → Discuss

## Important Notes for Claude Code

### Files You Work With
- `aiql.json` - Read this first! Contains all setup info
- Source file (from aiql.json) - Write SQL queries here
- Output file (from aiql.json) - Read results from here

### What You Should Do
- Always read aiql.json to understand the current setup
- Write clear, well-commented SQL queries
- Tell user to click "Run SQL" after writing queries
- Read and analyze results from the output file
- Suggest optimizations and next steps

### What You Should NOT Do
- Never try to execute SQL yourself (user does this via AIQL)
- Never try to connect to databases directly
- Never include passwords in any files
- Never modify aiql.json (AIQL manages this)

## Example Session

```
User: "What tables exist in this database?"

Claude Code:
1. Reads aiql.json
2. Sees dbType is "mysql"
3. Writes to sourceFile:
   -- Show all tables in database
   SHOW TABLES;
4. Says: "I've written a query to list all tables. Click 'Run SQL' (F5) to execute it."

User: *clicks Run SQL button*

AIQL: *executes query, writes results to outputFile*

Claude Code:
1. Reads outputFile
2. Sees list of tables
3. Says: "Your database has 15 tables: users, products, orders, ..."
4. Suggests: "Would you like to see the structure of any specific table?"
```

## File Locations

Current working directory: {}
- aiql.json: Configuration handshake file
- cc-aiql-manual.yaml: This guide file

User's home directory (~/.aiql/):
- profiles.json: Connection profiles (contains passwords - never read this)
- history.db: File/command history (you don't need this)
- active.json: Active profile info (you don't need this)

## Keyboard Shortcuts for User

- F5 or Ctrl+R: Run SQL query
- Ctrl+S: Save current tab

## Profile Types

- **postgresql**: PostgreSQL database (uses psql command)
- **mysql**: MySQL database (uses mysql command)
- **mariadb**: MariaDB database (uses mysql command)
- **api-remote**: Remote API endpoint (uses HTTP POST to execute SQL)

## Tips for Claude Code

1. **Always check aiql.json first** - It tells you everything about the current setup
2. **Write defensive SQL** - Include error handling and comments
3. **Explain your queries** - Help user understand what the SQL does
4. **Suggest optimizations** - If you see inefficient patterns, mention them
5. **Be patient** - Wait for user to run queries, don't try to execute them yourself

## Need Help?

- Website: https://elazarpimentel.com/en/tools/aiql
- GitHub: https://github.com/ElazarPimentel/aiql
""".format(self.cwd)

            with open(guide_path, 'w') as f:
                f.write(guide_content)

            # Show success message
            success_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Claude Code Guide Generated!"
            )
            success_dialog.format_secondary_text(
                f"Created: {guide_path}\n\n"
                "Claude Code can now read this file to understand how to use AIQL."
            )
            success_dialog.run()
            success_dialog.destroy()

            print(f"Generated Claude Code guide: {guide_path}")

        except Exception as e:
            error_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Error generating guide: {e}"
            )
            error_dialog.run()
            error_dialog.destroy()

    def execute_sql(self, sql_content, profile):
        """Execute SQL and write output to Tab2"""
        db_type = profile.get('db_type', 'postgresql')
        statements = self.parse_sql_statements(sql_content)
        
        if not statements:
            error_dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="No valid SQL statements found"
            )
            error_dialog.run()
            error_dialog.destroy()
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d / %H:%M:%S")
        output_file = profile.get('output_file')
        output_file_display = self.path_with_tilde(output_file) if output_file else 'N/A'

        output_content = f"=== SQL Results {timestamp} ===\n"
        output_content += f"Profile: {self.current_profile}\n"
        output_content += f"Database: {profile.get('database')} @ {profile.get('host')}\n"
        output_content += f"Output file: {output_file_display}\n\n"
        
        overall_success = True
        
        for i, statement in enumerate(statements, 1):
            if "SELECT '===" in statement and "===' as" in statement:
                section_match = re.search(r"SELECT '(=== [^=]+ ===)'", statement)
                if section_match:
                    section_name = section_match.group(1)
                    output_content += f"\n{section_name}\n{'='*len(section_name)}\n"
                    continue
            
            output_content += f"SQL Query:\n{statement}\n\nResult:\n"

            # Time the execution
            start_time = time.time()
            return_code, stdout, stderr = self.execute_sql_statement(statement, profile)
            execution_time = time.time() - start_time

            if stdout.strip():
                output_content += f"{stdout}\n"

            if stderr.strip():
                output_content += f"ERROR: {stderr}\n"

            if return_code != 0:
                overall_success = False
                output_content += f"FAILED (code: {return_code})\n"

            # Add execution time
            output_content += f"Execution time: {execution_time:.3f}s\n"
            output_content += "\n" + "-"*40 + "\n"
        
        output_content += f"\n=== SUMMARY ===\nQueries: {len(statements)} | Status: {'SUCCESS' if overall_success else 'ERROR'}\n"
        
        # Write to profile's output file
        output_file = profile.get('output_file')
        if output_file:
            try:
                output_path = Path(output_file)
                # Resolve relative paths relative to cwd
                if not output_path.is_absolute():
                    output_path = Path(self.cwd) / output_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                print(f"Results written to: {output_file}")
            except Exception as e:
                print(f"Error writing output: {e}")
        
        # Update Tab2 buffer if it's loaded
        buffer = self.tab2_view.get_buffer()
        buffer.set_text(output_content)
        buffer.set_modified(False)

        # Switch to Tab2
        self.notebook.set_current_page(1)

        # Beep and flash window if enabled (do it here, not in reload_tab2_and_switch)
        if self.beep_on_output:
            self.notify_output_ready()

        # Set button state based on execution result
        if overall_success:
            self.set_run_sql_button_state('red')  # Success - results ready
            print(f"SQL executed successfully")
        else:
            self.set_run_sql_button_state('pink')  # Error occurred
            print(f"SQL execution completed with errors")

    def parse_sql_statements(self, content):
        """Parse SQL file into individual statements, handling DELIMITER and strings properly"""
        statements = []
        current_statement = []
        in_single_quote = False
        in_double_quote = False
        current_delimiter = ';'  # Track current delimiter

        lines = content.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments (only if not in a string)
            if line.startswith('--') and not in_single_quote and not in_double_quote:
                continue

            # Check for DELIMITER command (case-insensitive)
            if line.upper().startswith('DELIMITER ') and not in_single_quote and not in_double_quote:
                # Extract new delimiter
                new_delimiter = line.split(None, 1)[1].strip()
                current_delimiter = new_delimiter
                # Don't add DELIMITER commands to statements - they're directives
                continue

            current_statement.append(line)

            # Check if this line ends a statement (delimiter outside of quotes)
            i = 0
            while i < len(line):
                char = line[i]

                # Toggle quote tracking
                if char == "'" and not in_double_quote:
                    # Check if it's escaped
                    if i > 0 and line[i-1] == '\\':
                        i += 1
                        continue
                    in_single_quote = not in_single_quote
                elif char == '"' and not in_single_quote:
                    # Check if it's escaped
                    if i > 0 and line[i-1] == '\\':
                        i += 1
                        continue
                    in_double_quote = not in_double_quote
                elif not in_single_quote and not in_double_quote:
                    # Check if we've hit the current delimiter
                    delimiter_match = True
                    for j, delim_char in enumerate(current_delimiter):
                        if i + j >= len(line) or line[i + j] != delim_char:
                            delimiter_match = False
                            break

                    if delimiter_match:
                        # Found statement terminator outside of quotes
                        # Remove the delimiter from the statement
                        statement_text = ' '.join(current_statement)
                        # Strip the delimiter from the end
                        if statement_text.endswith(current_delimiter):
                            statement_text = statement_text[:-len(current_delimiter)].strip()

                        if statement_text:
                            statements.append(statement_text)
                        current_statement = []
                        in_single_quote = False
                        in_double_quote = False
                        break

                i += 1

        # Handle any remaining statement without delimiter
        if current_statement:
            statement = ' '.join(current_statement)
            if statement.strip():
                statements.append(statement.strip())

        return statements

    def execute_sql_statement(self, sql_statement, profile):
        """Execute a single SQL statement and return results"""
        db_type = profile.get('db_type', 'postgresql')

        if db_type == 'api-remote':
            # Remote API execution - run in thread to keep GUI responsive
            try:
                import requests

                api_url = profile.get('host', '')
                api_key = profile.get('password', '')

                if not api_url or not api_key:
                    return 1, "", "API URL or API key not configured in profile"

                # Container for thread result [returncode, stdout, stderr]
                result_container = [None, None, None]
                exception_container = [None]

                def api_request_thread():
                    """Run API request in background thread"""
                    try:
                        response = requests.post(
                            api_url,
                            json={'query': sql_statement},
                            headers={'X-API-Key': api_key},
                            timeout=30
                        )

                        if response.status_code == 200:
                            data = response.json()

                            # Format results as readable text
                            output_lines = []

                            for idx, result in enumerate(data.get('results', []), 1):
                                if result.get('type') == 'select':
                                    # SELECT query results
                                    rows = result.get('rows', [])
                                    fields = result.get('fields', [])

                                    if rows:
                                        # Table format
                                        output_lines.append('\t'.join(fields))
                                        for row in rows:
                                            output_lines.append('\t'.join(str(row.get(f, '')) for f in fields))
                                    else:
                                        output_lines.append('(Empty result set)')

                                elif result.get('type') == 'write':
                                    # INSERT/UPDATE/DELETE results
                                    affected = result.get('affected_rows', 0)
                                    insert_id = result.get('insert_id')

                                    if insert_id:
                                        output_lines.append(f'Query OK, {affected} row(s) affected (Insert ID: {insert_id})')
                                    else:
                                        output_lines.append(f'Query OK, {affected} row(s) affected')

                            output_text = '\n'.join(output_lines)
                            result_container[0] = 0
                            result_container[1] = output_text
                            result_container[2] = ''

                        else:
                            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                            error_msg = error_data.get('error', f'HTTP {response.status_code}')
                            details = error_data.get('details', '')
                            result_container[0] = 1
                            result_container[1] = ""
                            result_container[2] = f"{error_msg}\n{details}" if details else error_msg

                    except requests.exceptions.Timeout:
                        exception_container[0] = "Timeout: API request took longer than 30 seconds"
                    except requests.exceptions.RequestException as e:
                        exception_container[0] = f"API connection error: {str(e)}"
                    except Exception as e:
                        exception_container[0] = f"API error: {str(e)}"

                # Start API request in background thread
                thread = threading.Thread(target=api_request_thread, daemon=True)
                thread.start()

                # Poll for completion while processing GTK events to keep GUI responsive
                start_time = time.time()
                timeout = 35  # Slightly longer than API timeout to catch timeout errors

                while thread.is_alive():
                    # Process pending GTK events to keep GUI responsive
                    while Gtk.events_pending():
                        Gtk.main_iteration()

                    # Check for timeout
                    if time.time() - start_time > timeout:
                        return 1, "", "Timeout: API request took longer than expected"

                    # Small sleep to avoid busy-waiting
                    time.sleep(0.1)

                # Wait for thread to fully complete
                thread.join(timeout=1)

                # Check for exceptions
                if exception_container[0]:
                    return 1, "", exception_container[0]

                # Return result from thread
                if result_container[0] is not None:
                    return result_container[0], result_container[1], result_container[2]
                else:
                    return 1, "", "API request completed but no result was returned"

            except Exception as e:
                return 1, "", f"Unexpected error: {str(e)}"

        elif db_type == 'postgresql':
            connection_url = f"postgresql://{profile['username']}:{profile['password']}@{profile['host']}:{profile['port']}/{profile['database']}"
            command = ["psql", connection_url, "-c", sql_statement]
        elif db_type in ['mysql', 'mariadb']:
            command = [
                "mysql",
                f"--host={profile['host']}",
                f"--port={profile['port']}",
                f"--user={profile['username']}",
                f"--password={profile['password']}",
                profile['database']
            ]
        else:
            return 1, "", f"Unsupported database type: {db_type}"

        try:
            # Use Popen with polling to keep GUI responsive
            # For MySQL/MariaDB, send SQL via stdin to support DELIMITER commands
            if db_type in ['mysql', 'mariadb']:
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Write SQL to stdin and close it
                process.stdin.write(sql_statement)
                process.stdin.close()
            else:
                # PostgreSQL and others don't need stdin
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            # Poll every 0.1 seconds and process GTK events to prevent "not responding"
            start_time = time.time()
            timeout = 30

            while process.poll() is None:
                # Process pending GTK events to keep GUI responsive
                while Gtk.events_pending():
                    Gtk.main_iteration()

                # Check for timeout
                if time.time() - start_time > timeout:
                    process.kill()
                    return 1, "", "Timeout: SQL execution took longer than 30 seconds"

                # Small sleep to avoid busy-waiting
                time.sleep(0.1)

            # Get output after process completes
            # Note: stdin is already closed for MySQL/MariaDB, so just read outputs
            stdout = process.stdout.read() if process.stdout else ""
            stderr = process.stderr.read() if process.stderr else ""
            return process.returncode, stdout, stderr

        except Exception as e:
            return 1, "", f"Error: {str(e)}"

    def on_tab1_changed(self, buffer):
        """Auto-save Tab01 when content changes (debounced)"""
        if self.tab1_file:
            # Cancel previous timeout
            if self.tab1_save_timeout:
                GLib.source_remove(self.tab1_save_timeout)
            # Set new timeout
            self.tab1_save_timeout = GLib.timeout_add(self.AUTOSAVE_DELAY_MS, self.save_tab1)
            
    def on_tab2_changed(self, buffer):
        """(Disabled) Auto-save Tab02 - manual save only"""
        return False
            
    def save_tab1(self):
        """Save Tab01 content"""
        self.tab1_save_timeout = None  # Clear timeout ID
        
        if not self.tab1_file:
            return False
            
        buffer = self.tab1_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        text = buffer.get_text(start, end, True)
        
        try:
            with open(self.tab1_file, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"Error saving Tab01: {e}")
            
        return False
        
    def save_tab2(self):
        """Save Tab02 content (manual only)"""
        self.tab2_save_timeout = None
        if not self.tab2_file:
            return False
        buffer = self.tab2_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        text = buffer.get_text(start, end, True)
        # Avoid self-triggered monitor events while saving
        if self.tab2_monitor:
            self.tab2_monitor.cancel()
        self.tab2_is_saving = True
        try:
            with open(self.tab2_file, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"Error saving Tab02: {e}")
        finally:
            # Re-enable file monitor and clear saving flag
            file = Gio.File.new_for_path(self.tab2_file)
            self.tab2_monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
            self.tab2_monitor.connect("changed", self.on_tab2_file_changed)
            self.tab2_is_saving = False
        return False
        
    def on_open_tab1(self, widget):
        """Open file dialog for Tab01"""
        dialog = Gtk.FileChooserDialog(
            title="Open file in Tab01",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            self.load_file_to_tab1(filepath)
            self.save_recent_file(1, filepath)
            
        dialog.destroy()
        
    def on_open_tab2(self, widget):
        """Open file dialog for Tab02"""
        dialog = Gtk.FileChooserDialog(
            title="Open file in Tab02",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            self.load_file_to_tab2(filepath)
            self.save_recent_file(2, filepath)
            
        dialog.destroy()
        
    def load_file_to_tab1(self, filepath):
        """Load file content into Tab01"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            buffer = self.tab1_view.get_buffer()
            buffer.set_text(content)
            buffer.set_modified(False)
            
            self.tab1_file = filepath
            
            # Setup file monitor
            if self.tab1_monitor:
                self.tab1_monitor.cancel()
            file = Gio.File.new_for_path(filepath)
            self.tab1_monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
            self.tab1_monitor.connect("changed", self.on_tab1_file_changed)
            
            # Update tab label
            filename = os.path.basename(filepath)
            label = self.notebook.get_tab_label(self.tab1_scroll)
            label.set_text(f"Tab01: {filename}")

            # Update active.json
            self.update_active_json()

        except Exception as e:
            print(f"Error loading file to Tab01: {e}")
            
    def load_file_to_tab2(self, filepath):
        """Load file content into Tab02"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            buffer = self.tab2_view.get_buffer()
            buffer.set_text(content)
            buffer.set_modified(False)
            
            self.tab2_file = filepath
            
            # Setup file monitor
            if self.tab2_monitor:
                self.tab2_monitor.cancel()
            file = Gio.File.new_for_path(filepath)
            self.tab2_monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
            self.tab2_monitor.connect("changed", self.on_tab2_file_changed)
            
            # Update tab label
            filename = os.path.basename(filepath)
            label = self.notebook.get_tab_label(self.tab2_scroll)
            label.set_text(f"Tab02: {filename}")

            # Update active.json
            self.update_active_json()

        except Exception as e:
            print(f"Error loading file to Tab02: {e}")
            
    def on_tab1_file_changed(self, monitor, file, other_file, event_type):
        """Handle Tab01 file changes (external)"""
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            GLib.idle_add(self.reload_tab1)
            
    def on_tab2_file_changed(self, monitor, file, other_file, event_type):
        """Handle Tab02 file changes (external) - auto-reload and switch"""
        if event_type == Gio.FileMonitorEvent.CHANGES_DONE_HINT and not self.tab2_is_saving:
            # Debounce multiple rapid events: schedule one reload if none pending
            if self.tab2_pending_reload_id is None:
                self.tab2_pending_reload_id = GLib.timeout_add(250, self.reload_tab2_and_switch)
            
    def reload_tab1(self):
        """Reload Tab01 from disk"""
        if self.tab1_file and os.path.exists(self.tab1_file):
            try:
                # Temporarily disable file monitor to prevent self-triggering
                if self.tab1_monitor:
                    self.tab1_monitor.cancel()

                with open(self.tab1_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                buffer = self.tab1_view.get_buffer()

                # Check if content actually changed
                start_iter = buffer.get_start_iter()
                end_iter = buffer.get_end_iter()
                current_text = buffer.get_text(start_iter, end_iter, True)

                if current_text != content:
                    # Save current scroll position
                    vadj = self.tab1_scroll.get_vadjustment()
                    scroll_pos = vadj.get_value()

                    buffer.set_text(content)
                    buffer.set_modified(False)

                    # Restore scroll position after a short delay
                    GLib.timeout_add(50, lambda: vadj.set_value(scroll_pos))

                    # Set Run SQL button to green (ready) when Tab01 changes
                    self.set_run_sql_button_state('green')

                # Re-enable file monitor
                file = Gio.File.new_for_path(self.tab1_file)
                self.tab1_monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
                self.tab1_monitor.connect("changed", self.on_tab1_file_changed)

            except Exception as e:
                print(f"Error reloading Tab01: {e}\"")
        return False
        
    def reload_tab2_and_switch(self):
        """Reload Tab02 from disk and switch to it"""
        # Clear pending reload flag now that we're handling it
        self.tab2_pending_reload_id = None
        if self.tab2_file and os.path.exists(self.tab2_file):
            try:
                # Temporarily disable file monitor to prevent self-triggering
                if self.tab2_monitor:
                    self.tab2_monitor.cancel()

                with open(self.tab2_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                buffer = self.tab2_view.get_buffer()

                # Check if content actually changed
                start_iter = buffer.get_start_iter()
                end_iter = buffer.get_end_iter()
                current_text = buffer.get_text(start_iter, end_iter, True)

                if current_text != content:
                    # Save current scroll position
                    vadj = self.tab2_scroll.get_vadjustment()
                    scroll_pos = vadj.get_value()

                    buffer.set_text(content)
                    buffer.set_modified(False)

                    # Restore scroll position after a short delay
                    GLib.timeout_add(50, lambda: vadj.set_value(scroll_pos))

                    # Switch to Tab02 to show the new content
                    self.notebook.set_current_page(1)

                    # Note: Beep is now triggered in execute_sql() instead of here
                    # to avoid duplicate beeps and ensure it works even when file content
                    # is already up-to-date in buffer

                # Re-enable file monitor
                file = Gio.File.new_for_path(self.tab2_file)
                self.tab2_monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, None)
                self.tab2_monitor.connect("changed", self.on_tab2_file_changed)

            except Exception as e:
                print(f"Error reloading Tab02: {e}")
        return False
        
    def save_recent_file(self, tab_number, filepath):
        """Save recently opened file to database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Remove if already exists
                cursor.execute(
                    'DELETE FROM recent_files WHERE tab_number = ? AND file_path = ? AND working_dir = ?',
                    (tab_number, filepath, str(self.cwd))
                )

                # Insert new record
                cursor.execute(
                    'INSERT INTO recent_files (tab_number, file_path, working_dir) VALUES (?, ?, ?)',
                    (tab_number, filepath, str(self.cwd))
                )
                
                # Keep only last MAX_RECENT_FILES
                cursor.execute('''
                    DELETE FROM recent_files
                    WHERE tab_number = ? AND working_dir = ? AND id NOT IN (
                        SELECT id FROM recent_files
                        WHERE tab_number = ? AND working_dir = ?
                        ORDER BY last_opened DESC LIMIT ?
                    )
                ''', (tab_number, str(self.cwd), tab_number, str(self.cwd), self.MAX_RECENT_FILES))
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error saving recent file: {e}")
        
    def load_recent_files(self):
        """Load most recent files on startup"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Tab 1
                cursor.execute('''
                    SELECT file_path FROM recent_files
                    WHERE tab_number = 1 AND working_dir = ?
                    ORDER BY last_opened DESC LIMIT 1
                ''', (str(self.cwd),))
                result = cursor.fetchone()
                if result and os.path.exists(result[0]):
                    self.load_file_to_tab1(result[0])

                # Tab 2
                cursor.execute('''
                    SELECT file_path FROM recent_files
                    WHERE tab_number = 2 AND working_dir = ?
                    ORDER BY last_opened DESC LIMIT 1
                ''', (str(self.cwd),))
                result = cursor.fetchone()
                if result and os.path.exists(result[0]):
                    self.load_file_to_tab2(result[0])
        except sqlite3.Error as e:
            print(f"Database error loading recent files: {e}")
        
    def show_recent_tab1(self, widget):
        """Show recent files dialog for Tab01"""
        self.show_recent_dialog(1)
        
    def show_recent_tab2(self, widget):
        """Show recent files dialog for Tab02"""
        self.show_recent_dialog(2)
        
    def show_recent_dialog(self, tab_number):
        """Show dialog with recent files for specified tab"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT file_path FROM recent_files
                    WHERE tab_number = ? AND working_dir = ?
                    ORDER BY last_opened DESC LIMIT ?
                ''', (tab_number, str(self.cwd), self.MAX_RECENT_FILES))
                
                recent_files = [row[0] for row in cursor.fetchall() if os.path.exists(row[0])]
        except sqlite3.Error as e:
            print(f"Database error loading recent files: {e}")
            recent_files = []
        
        if not recent_files:
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="No recent files"
            )
            dialog.run()
            dialog.destroy()
            return
            
        # Create selection dialog
        dialog = Gtk.Dialog(
            title=f"Recent Files - Tab{tab_number:02d}",
            parent=self,
            flags=0
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.OK
        )
        
        box = dialog.get_content_area()
        
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        for filepath in recent_files:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=filepath)
            label.set_xalign(0)
            row.add(label)
            listbox.add(row)
            
        box.pack_start(listbox, True, True, 10)
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected = listbox.get_selected_row()
            if selected:
                filepath = recent_files[selected.get_index()]
                if tab_number == 1:
                    self.load_file_to_tab1(filepath)
                else:
                    self.load_file_to_tab2(filepath)
                self.save_recent_file(tab_number, filepath)
                
        dialog.destroy()
        
    def on_beep_toggled(self, widget):
        """Handle Beep checkbox toggle"""
        self.beep_on_output = widget.get_active()
        print(f"Beep checkbox toggled: {self.beep_on_output}", flush=True)

    def notify_output_ready(self):
        """
        Notify user that output is ready - beep and flash window

        Uses multiple notification methods:
        1. Terminal bell (\\a) - works in most terminals
        2. Multiple system sound attempts (try different paths)
        3. Window urgency hint - flashes taskbar when not in foreground
        4. Floating notification window - blinks red 4 times
        """
        print("🔔 OUTPUT READY - Beep notification triggered!", flush=True)

        # Terminal bell - simple and usually works
        print('\a', flush=True)

        # Try Gdk.beep() first
        try:
            Gdk.beep()
        except Exception as e:
            print(f"Gdk.beep() failed: {e}", flush=True)

        # Try to play system sound (non-blocking, try multiple paths)
        sound_paths = [
            '/usr/share/sounds/freedesktop/stereo/complete.oga',
            '/usr/share/sounds/freedesktop/stereo/bell.oga',
            '/usr/share/sounds/freedesktop/stereo/message.oga',
            '/usr/share/sounds/ubuntu/stereo/message.ogg'
        ]

        for sound_path in sound_paths:
            try:
                subprocess.Popen(
                    ['paplay', sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"Playing sound: {sound_path}", flush=True)
                break  # Success, don't try other paths
            except FileNotFoundError:
                continue  # Try next path
            except Exception:
                continue  # Try next path

        # Flash window in taskbar if not in foreground
        # This makes the window flash/highlight to grab attention
        print("Setting urgency hint...", flush=True)
        self.set_urgency_hint(True)

        # Blink the floating notification window red 4 times
        print("🚨 Blinking notification window red...", flush=True)
        self.notification_window.blink_red(times=4)

        # Clear urgency hint after 3 seconds or when window gets focus
        def clear_urgency():
            self.set_urgency_hint(False)
            return False
        GLib.timeout_add(3000, clear_urgency)

    def toggle_dark_theme(self, widget):
        """Toggle between light and dark theme"""
        self.dark_theme = widget.get_active()

        # Apply to GTK settings
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", self.dark_theme)

        # Apply to editor buffers
        self.apply_editor_theme(self.tab1_view.get_buffer())
        self.apply_editor_theme(self.tab2_view.get_buffer())

    def show_data_storage_info(self, widget):
        """Show information about what data AIQL stores and where"""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="AIQL Data Storage Information"
        )

        info_text = f"""AIQL stores configuration files in two locations:

📁 User Configuration Directory (~/.aiql/):
  • profiles.json - Database connection profiles
    ⚠️ Contains passwords in plaintext - keep safe!
    ⚠️ Never commit this file to git repositories

  • history.db - SQLite database storing:
    - Recently opened files
    - Terminal command history
    ✅ Does NOT contain passwords or credentials

  • active.json - Currently active profile metadata
    Contains connection details but NO passwords

📁 Working Directory ({self.cwd}):
  • aiql.json - Current profile configuration
    ✅ Safe to commit - does NOT contain passwords
    This is the "handshake file" for Claude Code AI

  • cc-aiql-manual.yaml - Guide for Claude Code
    ✅ Safe to commit - documentation only

🔒 Security Recommendations:
  • Add profiles.json to .gitignore
  • Use api-remote mode for production databases
  • Always review SQL queries before executing
  • Keep ~/.aiql/ directory permissions restricted

📖 For more information:
  https://elazarpimentel.com/en/tools/aiql"""

        dialog.format_secondary_text(info_text)
        dialog.run()
        dialog.destroy()

    def show_about_dialog(self, widget):
        """Show About dialog with link to website"""
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self)
        dialog.set_modal(True)

        dialog.set_program_name("AIQL")
        dialog.set_version("5.3")
        dialog.set_comments(
            "AI-Assisted SQL Editor\n\n"
            "A collaborative database interface that bridges human users\n"
            "and AI assistants (like Claude Code) to work with databases together.\n\n"
            "AIQL is free and open source."
        )
        dialog.set_website("https://elazarpimentel.com/en/tools/aiql")
        dialog.set_website_label("Visit AIQL Website")
        dialog.set_authors(["Elazar Pimentel <elazar.pimentel@pensanta.com>"])
        dialog.set_copyright("Copyright © 2024-2025 Elazar Pimentel")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.set_logo_icon_name("applications-database")

        dialog.run()
        dialog.destroy()

    def on_quit(self, widget):
        """Clean up and quit"""
        # Cancel any pending save timeouts
        if self.tab1_save_timeout:
            GLib.source_remove(self.tab1_save_timeout)
        if self.tab2_save_timeout:
            GLib.source_remove(self.tab2_save_timeout)

        # Save any unsaved changes
        if self.tab1_file:
            self.save_tab1()
        if self.tab2_file:
            self.save_tab2()

        # Cancel file monitors
        if self.tab1_monitor:
            self.tab1_monitor.cancel()
        if self.tab2_monitor:
            self.tab2_monitor.cancel()

        # Close notification window
        if self.notification_window:
            self.notification_window.destroy()

        # Clear active.json on quit
        try:
            if self.active_json_path.exists():
                self.active_json_path.unlink()
        except Exception as e:
            print(f"Error removing active.json: {e}")

        Gtk.main_quit()

def main():
    app = AIQLApp()
    app.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()

