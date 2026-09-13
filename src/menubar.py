"""macOS menu bar (status bar) icon for the dashboard.

Runs inside the Tk main loop of the dashboard process. Menu actions are delivered by
AppKit on the main thread, so the callbacks may touch Tk widgets directly.
On non-macOS platforms (or if pyobjc is missing) `create_menubar` returns None.
"""
import os
import sys

import utils

try:
    import objc
    from AppKit import (
        NSApplication, NSImage, NSMenu, NSMenuItem, NSObject, NSStatusBar,
        NSVariableStatusItemLength, NSOnState, NSOffState,
        NSApplicationActivationPolicyAccessory,
    )
    AVAILABLE = sys.platform == "darwin"
except Exception:  # pragma: no cover - non-mac or pyobjc missing
    AVAILABLE = False

ICON_SIZE = 18
DOCK_GUARD_INTERVAL_MS = 300


def _nsapp():
    # Must only be called AFTER tkinter.Tk() exists: Tk installs its own NSApplication
    # subclass, and creating a plain NSApplication first makes Tk crash.
    return NSApplication.sharedApplication()


def activate_app():
    """Bring this (background-only) app to the front so Tk windows can take focus."""
    if not AVAILABLE:
        return
    try:
        _nsapp().activateIgnoringOtherApps_(True)
    except Exception as e:
        print(f"activate_app failed: {e}")


def hide_dock_icon():
    """Switch to the 'accessory' activation policy: no Dock icon, no Cmd-Tab entry.

    LSUIElement in Info.plist is not enough because Tk forces the 'regular' policy at
    init and again whenever it maps/unmaps a window. Call this after every show/hide."""
    if not AVAILABLE:
        return
    try:
        app = _nsapp()
        if app.activationPolicy() != NSApplicationActivationPolicyAccessory:
            app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except Exception as e:
        print(f"hide_dock_icon failed: {e}")


def install_dock_guard(root):
    """Periodically re-hides the Dock icon, catching resets Tk makes on its own."""
    if not AVAILABLE:
        return
    def tick():
        hide_dock_icon()
        try:
            root.after(DOCK_GUARD_INTERVAL_MS, tick)
        except Exception:
            pass  # root destroyed
    tick()


if AVAILABLE:

    class _MenuController(NSObject):
        """Objective-C target for the menu items + NSMenuDelegate for live refresh."""

        def initWithApp_(self, app):
            self = objc.super(_MenuController, self).init()
            if self is None:
                return None
            self.app = app
            self.items = {}
            return self

        # --- NSMenuDelegate ---
        def menuNeedsUpdate_(self, menu):
            self.refresh()

        def refresh(self):
            running = self.app.is_scheduler_running()
            self.items["status"].setTitle_("⚔️ 작전 수행 중" if running else "⚠️ 작전 중지")
            self.items["toggle"].setTitle_("임무 중지" if running else "임무 시작")
            self.items["autolaunch"].setState_(NSOnState if utils.get_autolaunch_status() else NSOffState)

        # --- actions (selector names end with ':' -> one trailing underscore) ---
        def openDashboard_(self, sender):
            self.app.show_window()

        def toggleScheduler_(self, sender):
            self.app.toggle_scheduler()

        def preview_(self, sender):
            self.app.preview()

        def openSettings_(self, sender):
            self.app.show_window()
            self.app.open_settings()

        def toggleAutolaunch_(self, sender):
            self.app.set_autolaunch(not utils.get_autolaunch_status())

        def quit_(self, sender):
            self.app.cleanup_and_exit()


class MenuBar:
    """Owns the NSStatusItem so it is not garbage collected."""

    def __init__(self, app):
        self.app = app
        self.controller = _MenuController.alloc().initWithApp_(app)
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self._set_icon()

        menu = NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)
        menu.setDelegate_(self.controller)

        def add(key, title, selector=None, enabled=True):
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, selector, "")
            if selector:
                item.setTarget_(self.controller)
            item.setEnabled_(enabled)
            menu.addItem_(item)
            self.controller.items[key] = item
            return item

        add("status", "작전 준비 완료", None, enabled=False)
        menu.addItem_(NSMenuItem.separatorItem())
        add("toggle", "임무 시작", "toggleScheduler:")
        add("preview", "미리보기", "preview:")
        menu.addItem_(NSMenuItem.separatorItem())
        add("dashboard", "작전 본부 열기", "openDashboard:")
        add("settings", "환경 설정...", "openSettings:")
        add("autolaunch", "맥북 시작 시 자동 연결", "toggleAutolaunch:")
        menu.addItem_(NSMenuItem.separatorItem())
        add("quit", "본부 완전 종료", "quit:")

        self.status_item.setMenu_(menu)
        self.menu = menu
        self.controller.refresh()

    def _set_icon(self):
        button = self.status_item.button()
        icon_path = os.path.join(utils.BUNDLED_ASSETS_DIR, "app_icon.png")
        try:
            image = NSImage.alloc().initWithContentsOfFile_(icon_path)
            if image is None:
                raise ValueError(f"cannot load {icon_path}")
            image.setSize_((ICON_SIZE, ICON_SIZE))
            button.setImage_(image)
            button.setToolTip_("귀살대 건강 관리")
        except Exception as e:
            print(f"Menu bar icon fallback (text): {e}")
            button.setTitle_("⚔️")

    def is_visible(self):
        """True once AppKit has placed the item in the menu bar (window has a size)."""
        try:
            frame = self.status_item.button().window().frame()
            return frame.size.width > 0 and frame.size.height > 0
        except Exception:
            return False

    def refresh(self):
        self.controller.refresh()

    def remove(self):
        try:
            NSStatusBar.systemStatusBar().removeStatusItem_(self.status_item)
        except Exception:
            pass


def create_menubar(app):
    """Returns a MenuBar for the given dashboard app, or None when unsupported."""
    if not AVAILABLE:
        return None
    try:
        return MenuBar(app)
    except Exception as e:
        print(f"Menu bar unavailable: {e}")
        return None
