import dearpygui.dearpygui as dpg
import os

from PIL import ImageGrab, ImageDraw
from pynput import mouse
    
spy_mode = True
color_value_RGB = True
current_cursor_position = [0, 0]
final_cursor_position = [0, 0]
log_list = []

def select_mode(sender, app_data):
    global spy_mode
    if app_data == "Log":
        spy_mode = False
        dpg.hide_item("spy_group")
        dpg.show_item("log_group")
        dpg.hide_item("enter_press_registry")
    else:
        spy_mode = True
        dpg.hide_item("log_group")
        dpg.show_item("spy_group")
        dpg.show_item("enter_press_registry")
    print("spy_mode", spy_mode)

def select_color_value(sender, app_data):
    global color_value_RGB
    if app_data == "HEX": 
        color_value_RGB = False
        dpg.configure_item("color_edit", display_mode = dpg.mvColorEdit_hex)
        for item in log_list:
            dpg.configure_item(item, display_mode = dpg.mvColorEdit_hex)
    else:
        color_value_RGB = True
        dpg.configure_item("color_edit", display_mode = dpg.mvColorEdit_rgb)
        for item in log_list:
            dpg.configure_item(item, display_mode = dpg.mvColorEdit_rgb)
    for item in ("color_value_log_radio", "color_value_spy_radio"):
        dpg.set_value(item, app_data)
    print("color_value_RGB", color_value_RGB)

def key_press(sender, app_data):
    if len(log_list) <= 9:    
        global final_cursor_position
        final_cursor_position = current_cursor_position
        screenshot_small = ImageGrab.grab(bbox = (int(final_cursor_position[0]/2 - 67), int(final_cursor_position[1]/2 - 67), int(final_cursor_position[0]/2 + 68), int(final_cursor_position[1]/2 + 68)))
        
        screenshot_small_edited = ImageDraw.Draw(screenshot_small)
        screenshot_small_edited.rectangle((49, 67, 59, 67), (255, 255, 255))
        screenshot_small_edited.rectangle((75, 67, 85, 67), (255, 255, 255))

        screenshot_small_edited.rectangle((67, 49, 67, 59), (255, 255, 255))
        screenshot_small_edited.rectangle((67, 75, 67, 85), (255, 255, 255))

        screenshot_small_edited.ellipse((59, 59, 75, 75))

        screenshot_small.save("screenshot_small.png")
        width, height, channels, data = dpg.load_image("screenshot_small.png")
        dpg.add_static_texture(width = width, height = height, default_value = data, parent = "texture_registry")
        dpg.configure_item("preview_image", texture_tag = dpg.last_item())
        if os.path.exists("screenshot_small.png"):
            os.remove("screenshot_small.png")
        else:
            print("The file does not exist")

        screenshot_large = ImageGrab.grab()
        pixel = screenshot_large.getpixel((final_cursor_position[0], final_cursor_position[1]))
        dpg.set_value("color_edit", pixel)

        print("final_cursor_position", final_cursor_position)

        create_log_entry(pixel)
    else:
        dpg.show_item("no_more_values_text")

def create_log_entry(pixel):
    if dpg.is_item_shown("no_log_text"):
        dpg.hide_item("no_log_text")
        dpg.add_radio_button(("RGB", "HEX"), parent = "log_group", horizontal = True, callback = select_color_value, tag = "color_value_log_radio")
        dpg.add_separator(parent = "log_group", tag = "log_separator")
        dpg.add_button(parent = "log_group", label = "Clear log", callback = delete_log_entry, tag = "log_button")

    dpg.add_color_edit((pixel), parent = "log_group", before = "color_value_log_radio", display_mode = dpg.mvColorEdit_rgb, no_alpha = True, no_tooltip = True, no_picker = True, no_label = True, width = 140)
    log_list.append(dpg.last_item())

def delete_log_entry():
    dpg.show_item("no_log_text")
    dpg.delete_item("color_value_log_radio")
    dpg.delete_item("log_separator")
    dpg.delete_item("log_button")
    for items in log_list:
        dpg.delete_item(items)
    log_list.clear()

def on_move(x, y):
    global current_cursor_position
    x_round = round(2 * x)
    y_round = round(2 * y)
    current_cursor_position = [x_round, y_round]
    print("current_cursor_position", current_cursor_position)

listener = mouse.Listener(on_move = on_move) 
listener.start()

################################################################################################################################################################
########## UI ##########
################################################################################################################################################################

def create_GUI():
    dpg.create_context()

    with dpg.texture_registry(tag = "texture_registry"):
        logo_width, logo_height, logo_channels, logo_data = dpg.load_image("rocket_monkey_logo.png")
        dpg.add_static_texture(width = logo_width, height = logo_height, default_value = logo_data, tag = "logo_texture")

    with dpg.handler_registry(tag = "enter_press_registry"):
        dpg.add_key_press_handler(key = 257, callback = key_press, tag = "key_press_handler_257")
        dpg.add_key_press_handler(key = 335, callback = key_press, tag = "key_press_handler_335")

    dpg.create_viewport(title = "Pixel Spy", always_on_top = True, resizable = False, width = 160, height = 320)

    with dpg.window(label = "Pixel Spy", tag = "main_window"):

        with dpg.menu_bar():
            dpg.add_radio_button(("Spy", "Log"), default_value = "Spy", callback = select_mode, tag = "mode_radio")

        with dpg.group(tag = "spy_group"):
            with dpg.group():
                dpg.add_text("ENTER to log color")
                dpg.add_separator()
            
            with dpg.group():
                dpg.add_color_edit((0, 0, 0, 0), display_mode = dpg.mvColorEdit_rgb, no_alpha = True, no_tooltip = True, no_picker = True, no_label = True, width = 140, tag = "color_edit")
                dpg.add_radio_button(("RGB", "HEX"), horizontal = True, callback = select_color_value, tag = "color_value_spy_radio")
                dpg.add_separator()
            
            with dpg.group():
                dpg.add_image_button("logo_texture", width = 135, height = 135, tag = "preview_image")
                dpg.add_separator()
                dpg.add_text("Maximum reached!", show = False, tag = "no_more_values_text")

        with dpg.group(tag = "log_group", show = False):
            dpg.add_text("No log to show", tag = "no_log_text")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

create_GUI()
