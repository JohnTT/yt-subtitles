from nicegui import ui
from tabs.home_tab import home_tab
from tabs.settings_tab import settings_tab

def main():
    # Define the tab headers
    with ui.tabs() as tabs:
        tab1 = ui.tab('Home')
        tab2 = ui.tab('Settings')

    # Match each tab to its content
    with ui.tab_panels(tabs, value=tab1):
        with ui.tab_panel(tab1):
            home_tab()

        with ui.tab_panel(tab2):
            settings_tab()

    ui.run()

if __name__ == '__main__':
    main()
