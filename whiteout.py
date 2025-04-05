import cv2
import numpy as np
import pyautogui
import time
import os
import subprocess
import time
from datetime import datetime
from pynput.mouse import Button, Controller
import math

debug=0
wait_time=2
max_tries=3
player_id=1

mouse = Controller()

def swipe(x1, y1, x2, y2, duration=1):
    """Simulates a swipe gesture by dragging the mouse."""
    '''https://stackoverflow.com/questions/9543397/creating-a-mouse-scroll-event-using-python - replace with scroll '''
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    steps = max(int(distance / 2), 20) 
    mouse.position = (x1, y1)  # Move to start position
    time.sleep(0.1)
    mouse.press(Button.left)  # Press mouse button
    for i in range(steps):
        new_x = x1 + (x2 - x1) * (i / steps)
        new_y = y1 + (y2 - y1) * (i / steps)
        mouse.position = (new_x, new_y)
        time.sleep(duration / steps)  
    time.sleep(0.1)
    mouse.position = (x2, y2)  # Drag to end position
    time.sleep(duration)
    mouse.release(Button.left)
    

def load_image(file_name, convert="Y"):
    """Loads an image file and returns the image variable."""
    image = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)  # Load with alpha if present
    if image is None:
        print(f"❌ Error: Could not load image '{file_name}'")

    if convert=="Y" and image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    return image
    
    
    
    # Load icons

def find_image(image, debug_name="", threshold=0.8, important=False, cnt_tries=5):
    """Find the target image on screen using template matching and click it if found."""
    #print (f"find_image {debug_name} {important}")
    
    for i in range(cnt_tries):
    # Take a screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to OpenCV format
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # Perform template matching
        result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        t=str(int(max_val*100))
        screenshot[0:image.shape[0],0:image.shape[1]] = image
        screenshot = cv2.putText(screenshot, t, (0,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Print confidence score

        x, y = max_loc
        h, w = image.shape[:2]
        
        if debug>0 or important:
            # Draw rectangle on matched area (for debugging)
            cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
            filename = f"debug/{timestamp}_{debug_name}.png"
            cv2.imwrite(filename, screenshot)
    #        print(f"🔍 Debug image saved: {filename}")

        # If confidence is above threshold, click the image
        if max_val >= threshold:
            click_x, click_y = x + w // 2, y + h // 2


            return click_x, click_y
        
    return None, None

def find_and_click(image, debug_name="", threshold=0.7, important=False, cnt_tries=5):
    """Find the target image on screen using template matching and click it if found."""
    # Perform template matching
    print(debug_name)
    
    click_x, click_y = find_image(image, debug_name, threshold, important, cnt_tries)
    
    if click_x is not None:

        #print(f"✅ Target found at ({click_x}, {click_y}), clicking...")
        pyautogui.click(click_x, click_y)
        print("    ✅ Success");
        return True
    else:
        print("    ❌ Target not found.")
        return False

def click_anywhere():
    find_and_click(click_anywhere_img, "   Anywhere", 0.5, False, 10)
    
def collect_exploration():
    print("Collecting exploration")
    print("   ❌ Click exploration")
    if find_and_click(exploration_img, "   Exploration") or find_and_click(exploration2_img, "   Exploration2"):
        time.sleep(wait_time)
        print("   ❌ Click Claim")
    
        if find_and_click(exploration_claim_img, "   Claim in Exploration",  0.9):
            time.sleep(wait_time)
            print("   ❌ Click Confirm Claim")
            if find_and_click(exploration_claim_confirm_img, "   Confirm Claim in Exploration", 0.7, True):
                time.sleep(wait_time)
                print("   ❌ Click Anywhere")
                click_anywhere()
            time.sleep(wait_time)
            print("   ❌ Click Exploration back")

            find_and_click(exploration_back_img, "   Back in Exploration")
        else:            
            print("   ❌ Click Exploration back")
            find_and_click(exploration_back_img, "   Back in Exploration")

def click_help():
    print("❌  Clicking help")

    find_and_click(help_hand_img, "Help", 0.8)

def collect_rewards():
    print("❌  Collecting rewards")

    if find_and_click(left_bar_img, "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        print("   ❌ Click online rewards")
        if find_and_click(online_rewards_img, "   online rewards in a bar", 0.9):
            time.sleep(wait_time)
            print("   ❌ Click online reward collection")
            if find_and_click(online_reward_img, "   online reward"):
                time.sleep(wait_time)
                click_anywhere()
        else: find_and_click(close_bar_img, "   close bar", 0.5)

def train_marksman():
    print("❌ Train marksman")

    if find_and_click(left_bar_img, "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        print("   ❌ Click marksman completed")
        if find_and_click(marksman_completed_img, "   marksman completed in a bar", 0.9) or find_and_click(marksman_idle_img, "   marksman idle in a bar", 0.9):
                
            time.sleep(wait_time)
            try_number=1
            while not find_and_click(marksman_click_img, "   marksman click") and try_number<max_tries:
                time.sleep(wait_time*0.2)
                try_number=try_number+1
            
            time.sleep(wait_time)
            if find_and_click(marksman_camp_click_img, "   marksman camp click"):
                time.sleep(wait_time)
                if find_and_click(train_img, "   train click"):
                    time.sleep(2*wait_time)
                    if find_and_click(troops_upgrade_img, "   troops upgrade"):
                        time.sleep(wait_time)
                        find_and_click(troops_upgrade_confirm_img, "   troops upgrade confirm")
                        time.sleep(wait_time)
                        find_and_click(troops_promotion_img, "   troops promotion")
                        time.sleep(wait_time)
                    elif find_and_click(train_button_img, "   train button click"):
                          time.sleep(wait_time)
                          find_and_click(training_back_img, "   training_back click")
                    find_and_click(training_back_img, "   training_back click")
        else: find_and_click(close_bar_img, "   close bar", 0.5)
        

def train_infantry():
    print("❌ Train infantry")

    if find_and_click(left_bar_img, "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        print("   ❌ Click infantry completed")
        if find_and_click(infantry_completed_img, "   infantry completed in a bar", 0.9) or find_and_click(infantry_idle_img, "   infantry idle in a bar", 0.9):

            time.sleep(wait_time)
            try_number=1
            while not find_and_click(infantry_click_img, "   infantry click") and try_number<max_tries:
                time.sleep(wait_time*0.2)
                try_number=try_number+1
            
            time.sleep(wait_time)
            if find_and_click(infantry_camp_img, "   infantry camp click"):
                time.sleep(wait_time)
                if find_and_click(train_img, "   train click"):
                    time.sleep(2*wait_time)
                    if find_and_click(troops_upgrade_img, "   troops upgrade"):
                        time.sleep(wait_time)
                        find_and_click(troops_upgrade_confirm_img, "   troops upgrade confirm")
                        time.sleep(wait_time)
                        find_and_click(troops_promotion_img, "   troops promotion")
                        time.sleep(wait_time)
                    elif find_and_click(train_button_img, "   train button click"):
                          time.sleep(wait_time)
                          find_and_click(training_back_img, "   training_back click")
                    find_and_click(training_back_img, "   training_back click")
        else: find_and_click(close_bar_img, "   close bar", 0.5)
        

def train_lancers():
    print("❌ Train lancers")

    if find_and_click(left_bar_img, "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        print("   ❌ Click lancers completed")
        if find_and_click(lancers_completed_img, "   lancers completed in a bar", 0.9) or find_and_click(lancers_idle_img, "   lancers idle in a bar", 0.9):
                
            time.sleep(wait_time)
            try_number=1
            while not find_and_click(lancers_click_img, "   lancers click") and try_number<max_tries:
                time.sleep(wait_time*0.2)
                try_number=try_number+1
            time.sleep(wait_time)
            if find_and_click(lancers_camp_img, "   lancers camp click"):
                time.sleep(wait_time)
                
                if find_and_click(train_img, "   train click"):
                    time.sleep(2*wait_time)
                    if find_and_click(troops_upgrade_img, "   troops upgrade"):
                        time.sleep(wait_time)
                        find_and_click(troops_upgrade_confirm_img, "   troops upgrade confirm")
                        time.sleep(wait_time)
                        find_and_click(troops_promotion_img, "   troops promotion")
                        time.sleep(wait_time)
                    elif find_and_click(train_button_img, "   train button click"):
                          time.sleep(wait_time)
                          find_and_click(training_back_img, "   training_back click")
                    find_and_click(training_back_img, "   training_back click")
        else: find_and_click(close_bar_img, "   close bar", 0.5)

def radar_attack():
    if (find_and_click(view_img, "  view")):
        #time.sleep(wait_time)
        if (find_and_click(attack_img, "  attack")):                        
            print("  attack")
            #time.sleep(wait_time)
            if (find_and_click(march_queue_img, "  march queue")): # no troops
                        #time.sleep(wait_time)
                        find_and_click(march_queue_close_img, "  march queue close")
                        return 1
            if (find_image(attack_likely_to_prevail_img, "  attack likely to prevail") != (None, None) or find_image(attack_risky_img, "  attack risky") != (None, None)): #not too strong opponent
                #time.sleep(wait_time)
                if (find_and_click(march_deploy_img, "  deploy")):
                    #time.sleep(wait_time)
                    if (find_image(stamina_missing_img, "   stamina_missing") != (None, None)):
                        #time.sleep(wait_time)
                        find_and_click(stamina_missing_close_img, "   stamina_missing_close")
                        #time.sleep(wait_time)
                        find_and_click(exploration_back_img, "   exploration_back")
                        return 1
            else:#too strong
                find_and_click(attack_back_img, "  too strong - attack back")
                return 2
        else:
            #time.sleep(wait_time)
            if (find_and_click(march_queue_img, "  march queue")): # no troops
                #time.sleep(wait_time)
                find_and_click(march_queue_close_img, "  march queue close")
                return 1
    else:
        #time.sleep(wait_time)
        if (find_and_click(click_anywhere_img, "  click anywhere", 0.5)):
            return 0
        else:
            return 1
    return 1
            
def radar():
    print("Radar")
 #   find_and_click(world_img, "   world", 0.7)
 #   time.sleep(2*wait_time)
    devil_visited = False

    for i in range(5):
        if (find_and_click(radar_img, "  radar")):
            #time.sleep(2*wait_time)
            j=1
            while j<max_tries and find_image(location_radar_img," ...check location radar", 0.7, False, 10) == (None, None):
                j=j+1
                find_and_click(radar_img, "   radar")
                #time.sleep(wait_time)
            if (find_and_click(radar_tent_blue_img, "  radar tent blue", 0.9) or find_and_click(radar_tent_gold_img, "  radar tent gold", 0.9) or find_and_click(radar_tent_purple_img, "  radar tent purple", 0.9)):
                #time.sleep(wait_time)
                
                if (find_and_click(view_img, "  view")):
                    #time.sleep(wait_time)
                    find_and_click(radar_rescue_img, "  tent rescue")
                    if (find_and_click(march_queue_img, "  march queue")): # no troops
                        #time.sleep(wait_time)
                        find_and_click(march_queue_close_img, "  march queue close")
                        break
                    if (find_image(stamina_missing_img, "   stamina_missing") != (None, None)):
                        #time.sleep(wait_time)
                        find_and_click(stamina_missing_close_img, "   stamina_missing_close")
                        #time.sleep(wait_time)
                        find_and_click(exploration_back_img, "   exploration_back")
                        break
                else:
                    #time.sleep(wait_time)
                    if (find_and_click(click_anywhere_img, "  click anywhere", 0.5)):
                        break
            else:   
                if (find_and_click(radar_swords_blue_img, "  radar blue swords") or find_and_click(radar_swords_purple_img, "  radar purple swords") or find_and_click(radar_swords_golden_img, "  radar golden swords")):
                    #time.sleep(wait_time)
                    
                    if (find_and_click(view_img, "  view")):
                        #time.sleep(wait_time)
                        if (find_and_click(radar_explore_img, "  explore")):
                            #time.sleep(wait_time)
                            if (find_and_click(fight_img, "  fight")):
                                #time.sleep(5*wait_time)
                                find_and_click(fight_tap_anywhere_img, "  fight - tap anywhere", 0.7, False, 25)
                            else: #stamina_missing
                                #time.sleep(wait_time)
                                if (find_image(stamina_missing_img, "   stamina_missing") != (None, None)):
                                    #time.sleep(wait_time)
                                    find_and_click(stamina_missing_close_img, "   stamina_missing_close")
                                    #time.sleep(wait_time)
                                    find_and_click(exploration_back_img, "   exploration_back")
                                    break
                    else:
                        if (find_and_click(click_anywhere_img, "  click anywhere", 0.5)):
                            break
                else:
                    if find_and_click(radar_skull_blue_img, "  radar blue skull", 0.9) or find_and_click(radar_skull_purple_img, "  radar purple skull", 0.9) or find_and_click(radar_skull_golden_img, "  radar golden skull", 0.9):
                        #time.sleep(wait_time)
                        if radar_attack() >0:
                            break
                    elif find_and_click(radar_devil_img, "  radar devil") and not devil_visited:
                        #time.sleep(wait_time)
                        ret = radar_attack()
                        if ret == 1:
                            break
                        elif ret == 2:
                            devil_visited=True
                            break
                    else:
                        return False
    #time.sleep(wait_time)
    find_and_click(radar_exit_img, "  radar exit")
    #time.sleep(wait_time)
#    find_and_click(city_img, "   city", 0.7)
#    time.sleep(2*wait_time)
    return True
    

def recruitment() :
    print("Recruitment")
    if find_and_click(left_bar_img, "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        if (find_and_click(recruitment_img, "  recruitment", 0.9)):
            time.sleep(wait_time)
            find_and_click(recruit_free_img, "  recruit free")
            time.sleep(3*wait_time)
            find_and_click(recruit_tap_img, "  recruit tap")
            time.sleep(wait_time)
            find_and_click(radar_exit_img, "  exit")
        else: find_and_click(close_bar_img, "   close bar", 0.5)
            

def gathering() :
    print("Gathering")
#    find_and_click(world_img, "   world", 0.7)
#    time.sleep(4*wait_time)
    if find_and_click(map_search_img, "   map search"):
       time.sleep(wait_time)
       if find_and_click(map_iron_img, "   map iron"):
           time.sleep(wait_time)
           if find_and_click(search_img, "   search"):
               time.sleep(2*wait_time)
               find_and_click(gather_img, "   gather")
               time.sleep(wait_time)
               if (find_and_click(march_queue_img, "  march queue")): # no troops
                   time.sleep(wait_time)
                   find_and_click(march_queue_close_img, "  march queue close")
                   return None
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(add_hero_img, "   add hero")
               time.sleep(wait_time)
               find_and_click(iron_hero_img, "   iron hero")
               time.sleep(wait_time)
               find_and_click(assign_img, "   assign")
               time.sleep(wait_time)
               find_and_click(assign_close_img, "   assign close")
               time.sleep(2*wait_time)
               find_and_click(gather_deploy_img, "   deploy")
       time.sleep(wait_time)
       if find_and_click(map_coal_img, "   map coal"):
           time.sleep(wait_time)
           if find_and_click(search_img, "   search"):
               time.sleep(2*wait_time)
               find_and_click(gather_img, "   gather")
               time.sleep(wait_time)
               if (find_and_click(march_queue_img, "  march queue")): # no troops
                   time.sleep(wait_time)
                   find_and_click(march_queue_close_img, "  march queue close")
                   return None
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(add_hero_img, "   add hero")
               time.sleep(wait_time)
               #swipe(1015, 474, 1015, 374)
               find_and_click(coal_hero_img, "   coal hero")
               time.sleep(wait_time)
               find_and_click(assign_img, "   assign")
               time.sleep(wait_time)
               find_and_click(assign_close_img, "   assign close")
               time.sleep(2*wait_time)
               find_and_click(gather_deploy_img, "   deploy")
       if find_and_click(map_wood_img, "   map wood"):
           time.sleep(wait_time)
           if find_and_click(search_img, "   search"):
               time.sleep(2*wait_time)
               find_and_click(gather_img, "   gather")
               time.sleep(wait_time)
               if (find_and_click(march_queue_img, "  march queue")): # no troops
                   time.sleep(wait_time)
                   find_and_click(march_queue_close_img, "  march queue close")
                   return None
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(add_hero_img, "   add hero")
               time.sleep(wait_time)
               #swipe(1015, 474, 1015, 374)
               find_and_click(wood_hero_img, "   wood hero")
               time.sleep(wait_time)
               find_and_click(assign_img, "   assign")
               time.sleep(wait_time)
               find_and_click(assign_close_img, "   assign close")
               time.sleep(2*wait_time)
               find_and_click(gather_deploy_img, "   deploy")
       
       if find_and_click(map_meat_img, "   map meat"):
           time.sleep(wait_time)
           if find_and_click(search_img, "   search"):
               time.sleep(2*wait_time)
               find_and_click(gather_img, "   gather")
               time.sleep(wait_time)
               if (find_and_click(march_queue_img, "  march queue")): # no troops
                   time.sleep(wait_time)
                   find_and_click(march_queue_close_img, "  march queue close")
                   return None
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(remove_hero_img, "   remove hero")
               time.sleep(wait_time)
               find_and_click(add_hero_img, "   add hero")
               time.sleep(wait_time)
               #swipe(1015, 474, 1015, 374)
               find_and_click(meat_hero_img, "   meat hero")
               time.sleep(wait_time)
               find_and_click(assign_img, "   assign")
               time.sleep(wait_time)
               find_and_click(assign_close_img, "   assign close")
               time.sleep(2*wait_time)
               find_and_click(gather_deploy_img, "   deploy")
       
def healing():
    print("Heal")
#    find_and_click(world_img, "   world", 0.7)
#    time.sleep(4*wait_time)
    if find_and_click(heal_icon_img, "   heal icon"):
        time.sleep(wait_time)
        if find_and_click(heal_img, "   heal"):
            time.sleep(wait_time)
            find_and_click(help_img, "   help")
            click_help()
            time.sleep(wait_time)
#    find_and_click(city_img, "   city", 0.7)
#    time.sleep(2*wait_time)

def quick_healing():
    print("Quick heal")
    if find_and_click(heal_icon_img, "   heal icon"):
        while True:
            if find_and_click(heal_img, "   heal"):
                time.sleep(wait_time)
                find_and_click(help_img, "   help")
                click_help()
                time.sleep(wait_time)
            if find_image(location_chat_img, "...chat location") != (None, None):
                find_and_click(location_chat_exit_img, "...exit chat")
                time.sleep(wait_time)
                find_and_click(heal_icon_img, "   heal icon")
            
            

                    
def first_screen():
    print("First screen")
    find_and_click(reconnect_img, "   reconnect")
        #time.sleep(10*wait_time)
    if find_image(first_screen_ad_img, "...first screen", 0.7, False, 10)!= (None, None) or find_image(first_screen_ad2_img, "...first screen2", 0.7, False, 50)!= (None, None):
        find_and_click(add_cross_img, "  ad cross", 0.85)
        #time.sleep(wait_time)
        find_and_click(confirm_img, "  confirm")
        #time.sleep(wait_time)
    else:
        find_and_click(add_cross3_img, " ad cross 3", 0.85)
        find_and_click(add_cross4_img, " ad cross 4", 0.85)
        #time.sleep(2*wait_time)
        find_and_click(confirm_img, "  confirm", 0.7, False, 5)
        #time.sleep(wait_time)
    find_and_click(reklamy_img, "   reklamy", 0.7)

def read_mail():
    print("Mail")
    if find_and_click(mail_img, "   mail"):
        time.sleep(wait_time)
        i=1
        while i<max_tries and not find_image(location_mail_img," ...check location mail") != (None, None):
            i=i+1
            find_and_click(mail_img, "   mail")
            time.sleep(wait_time)
        find_and_click(mail_reports_img, "    mail reports", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_read_all_img, "    mail read all", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_tap_anywhere_img, "    mail tap anywhere", 0.7)
        time.sleep(wait_time)
        find_and_click(mail_system_img, "    mail system", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_read_all_img, "    mail read all", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_tap_anywhere_img, "    mail tap anywhere", 0.7)
        time.sleep(wait_time)
        find_and_click(mail_alliance_img, "    mail alliance", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_read_all_img, "    mail read all", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_tap_anywhere_img, "    mail tap anywhere", 0.7)
        time.sleep(wait_time)
        find_and_click(mail_wars_img, "    mail wars", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_read_all_img, "    mail read all", 0.85)
        time.sleep(wait_time)
        find_and_click(mail_tap_anywhere_img, "    mail tap anywhere", 0.7)
        time.sleep(wait_time)
        find_and_click(mail_exit_img, "    mail exit", 0.85)
        
def chief_order():
    print("Chief order")
    if find_and_click(chief_order_img, "   chief_order"):
        time.sleep(wait_time)
        i=1
        while i<max_tries and not find_image(location_chief_order_img," ...check location chief_order") != (None, None):
            i=i+1
            find_and_click(chief_order_img, "   chief_order")
            time.sleep(wait_time)
        if find_and_click(chief_order_rush_job_img, "   rush job", 0.9):
            time.sleep(wait_time)
            find_and_click(chief_order_enact_img, "   enact", 0.9)
            time.sleep(wait_time)
            click_anywhere()
        if find_and_click(chief_order_festives_img, "   festives", 0.9):
            time.sleep(wait_time)
            find_and_click(chief_order_enact_img, "   enact", 0.9)
        if find_and_click(chief_order_productivity_day_img, "   productivity day", 0.9):
            time.sleep(wait_time)
            find_and_click(chief_order_enact_img, "   enact", 0.9)
        if find_and_click(chief_order_urgent_mobilization_img, "   urgent mobilization", 0.9):
            time.sleep(wait_time)
            find_and_click(chief_order_enact_img, "   enact", 0.9)
        time.sleep(wait_time)
        find_and_click(chief_order_back_img, "   back", 0.9)
        time.sleep(wait_time)
        find_and_click(chief_order_back_img, "   back", 0.9)
        
def reset_location():
    print("Reset location")
    if find_image(world_img, "...city location") != (None, None):
        return None
    if find_image(city_img, "...world location") != (None, None):
        find_and_click(city_img, "...exit world")
    if find_image(location_chat_img, "...chat location") != (None, None):
        find_and_click(location_chat_exit_img, "...exit chat")
    if find_image(location_radar_img, "...radar location") != (None, None):
        find_and_click(radar_exit_img, "...exit radar")
    if find_image(location_exploration_img, "...exploration location") != (None, None):
        find_and_click(exploration_back_img, "...exit exploration")
    if find_image(location_infantry_training_img, "...infantry training location") != (None, None) or find_image(location_lancer_training_img, "...lancer training location") != (None, None) or find_image(location_marksman_training_img, "...marksman training location") != (None, None):
        find_and_click(training_back_img, "...training radar")
    if find_image(location_alliance_img, "...location_alliance") != (None, None):
        find_and_click(alliance_tech_back_img, "...alliance_tech_back")
        
def change_player(current_player_id):
    print("Change player")
    print(f"   current_id={current_player_id}")
    if current_player_id==1:#current player ID
        current_player = player_1_img
        target_player = player_2_img
    elif current_player_id==2:
        current_player = player_2_img
        target_player = player_1_img
    
    if find_and_click(current_player, "   enter profile", 0.7,True):
        #time.sleep(wait_time)
        find_and_click(chief_profile_settings_img, "   enter settings", 0.7, True)
        #time.sleep(wait_time)
        find_and_click(chief_profile_characters_img, "   enter characters", 0.7, True)
        #time.sleep(wait_time)
        if current_player_id==1:
            find_and_click(player_2_select_img, "   select player 2", 0.7, True)
            #time.sleep(wait_time)
        elif current_player_id==2:
            find_and_click(player_1_select_img, "   select player 1", 0.7, True)
            #time.sleep(wait_time)
        find_and_click(player_select_confirm_img, "   confirm player")
        if current_player_id == 1:
            current_player_id=2
        elif current_player_id==2:
            current_player_id=1
        time.sleep(wait_time*5)
    
    print(f"   new current_id={current_player_id}")
    
    #exit()
    return current_player_id
        
def alliance_tech():
    print("Alliance tech")
    try_number=1
    if find_and_click(left_bar_img, "   Left bar", 0.7):
        #time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        if find_and_click(alliance_contribution_img, "   alliance_contribution", 0.7):
            #time.sleep(wait_time)
            if not find_and_click(alliance_icon_img, "   alliance_icon", 0.7, False, 10):
                return None
            
            if not find_and_click(alliance_tech_img, "   alliance_tech", 0.7):
                return None
            #time.sleep(wait_time)
            find_and_click(alliance_tech_recommended_img, "   alliance_tech recommended", 0.7)
            #time.sleep(wait_time)
            try_number=1
            while find_image(alliance_cannot_contribute_img, "   alliance cannot contribute")==(None, None) and try_number<=25:
                find_and_click(alliance_contribute_img, "   alliance_contribute", 0.7)
                time.sleep(wait_time)
                try_number=try_number+1
            find_and_click(alliance_tech_close_img, "   alliance_tech close", 0.7)
            #time.sleep(wait_time)
            find_and_click(alliance_tech_back_img, "   alliance_tech back", 0.7)
            #time.sleep(wait_time)
            find_and_click(alliance_tech_back_img, "   alliance_tech back", 0.7)
            #time.sleep(wait_time)
            

help_hand_img = load_image ("icons/help_hand.png")
recall_troops_img = load_image ("icons/recall_troops.png")
world_img = load_image ("icons/world.png")
city_img = load_image ("icons/city.png")

add_cross_img = load_image ("icons/add_cross.png")
add_cross2_img = load_image ("icons/add_cross2.png")
add_cross3_img = load_image ("icons/add_cross3.png")
add_cross4_img = load_image ("icons/add_cross4.png")
exploration_img = load_image ("icons/exploration.png")
exploration2_img = load_image ("icons/exploration2.png")
click_anywhere_img = load_image ("icons/click_anywhere.png")

exploration_claim_img = load_image ("icons/exploration_claim.png")
exploration_claim_confirm_img = load_image ("icons/exploration_claim_confirm.png")
exploration_back_img = load_image ("icons/exploration_back.png")
left_bar_img = load_image ("icons/left_bar.png", "Y")
online_rewards_img = load_image ("icons/online_rewards.png")
online_reward_img = load_image ("icons/online_reward.png")
close_bar_img = load_image ("icons/close_bar.png")

marksman_completed_img = load_image ("icons/marksman_completed.png")
marksman_idle_img = load_image ("icons/marksman_idle.png")
marksman_click_img = load_image ("icons/marksman_click.png")
marksman_camp_click_img = load_image ("icons/marksman_camp_click.png")

infantry_completed_img = load_image ("icons/infantry_completed.png")
infantry_idle_img = load_image ("icons/infantry_idle.png")
infantry_click_img = load_image ("icons/infantry_click.png")
infantry_camp_img = load_image ("icons/infantry_camp.png")

lancers_completed_img = load_image ("icons/lancer_completed.png")
lancers_idle_img = load_image ("icons/lancer_idle.png")
lancers_click_img = load_image ("icons/lancer_click.png")
lancers_camp_img = load_image ("icons/lancer_camp.png")


training_back_img = load_image ("icons/training_back.png")

train_img = load_image ("icons/train2.png")
train_button_img = load_image ("icons/train_button.png")
troops_promotion_img = load_image ("icons/troops_promotion.png")
troops_upgrade_img = load_image ("icons/troops_upgrade.png")
troops_upgrade_confirm_img = load_image ("icons/troops_upgrade_confirm.png")

contribute_alliance_img = load_image ("icons/contribute_alliance.png")

radar_img = load_image ("icons/radar.png")
radar_devil_img = load_image ("icons/radar_devil.png")
radar_exit_img = load_image ("icons/radar_exit.png")
view_img = load_image ("icons/view.png")
attack_img = load_image ("icons/attack.png")
march_deploy_img = load_image ("icons/deploy.png")
attack_likely_to_prevail_img = load_image ("icons/attack_likely_to_prevail.png")
attack_risky_img = load_image ("icons/attack_risky.png")
attack_back_img = load_image ("icons/attack_back.png")

march_queue_img = load_image ("icons/march_queue.png")
march_queue_close_img = load_image ("icons/march_queue_close.png")

radar_tent_blue_img = load_image ("icons/tent_blue.png")
radar_tent_gold_img = load_image ("icons/tent_gold.png")
radar_tent_purple_img = load_image ("icons/tent_purple.png")

radar_skull_blue_img = load_image ("icons/skull_blue.png")
radar_skull_purple_img = load_image ("icons/skull_purple.png")
radar_skull_golden_img = load_image ("icons/skull_golden.png")

radar_swords_blue_img = load_image ("icons/swords_blue.png")
radar_swords_purple_img = load_image ("icons/swords_purple.png")
radar_swords_golden_img = load_image ("icons/swords_golden.png")

radar_rescue_img = load_image ("icons/tent_rescue.png")
radar_explore_img = load_image ("icons/radar_explore.png")
fight_img = load_image ("icons/fight.png")
fight_tap_anywhere_img = load_image ("icons/fight_tap_anywhere.png")
stamina_missing_img = load_image ("icons/stamina_missing.png")
stamina_missing_close_img = load_image ("icons/stamina_missing_close.png")


reklamy_img = load_image ("icons/reklamy.png")

recruitment_img = load_image ("icons/recruitment.png")

recruit_free_img = load_image ("icons/recruit_free.png")
recruit_tap_img = load_image ("icons/recruit_tap.png")

first_screen_ad_img = load_image ("icons/first_screen_ad.png")
first_screen_ad2_img = load_image ("icons/add_2nd_anniversary.png")


confirm_img = load_image ("icons/confirm.png")

reconnect_img = load_image ("icons/reconnect.png")

map_search_img = load_image ("icons/map_search.png")
map_coal_img = load_image ("icons/map_coal.png")
coal_hero_img = load_image ("icons/coal_hero.png")
map_iron_img = load_image ("icons/map_iron.png")
iron_hero_img = load_image ("icons/iron_hero.png")

map_wood_img = load_image ("icons/map_wood.png")
wood_hero_img = load_image ("icons/wood_hero.png")
map_meat_img = load_image ("icons/map_meat.png")
meat_hero_img = load_image ("icons/meat_hero.png")
search_img = load_image ("icons/search.png")

gather_img = load_image ("icons/gather.png")
remove_hero_img = load_image ("icons/remove_hero.png")
add_hero_img = load_image ("icons/add_hero.png")
assign_img = load_image ("icons/assign.png")
assign_close_img = load_image ("icons/assign_close.png")
gather_deploy_img = load_image ("icons/gather_deploy.png")

heal_img = load_image ("icons/heal.png")
help_img = load_image ("icons/help.png")
heal_icon_img = load_image ("icons/heal_icon.png")

mail_img = load_image("icons/mail.png")
mail_read_all_img = load_image("icons/mail_claim_and_read.png")
mail_system_img = load_image("icons/mail_system.png")
mail_alliance_img = load_image("icons/mail_alliance.png")
mail_wars_img = load_image("icons/mail_wars.png")
mail_exit_img = load_image("icons/mail_exit.png")
mail_reports_img = load_image("icons/mail_reports.png")
mail_tap_anywhere_img = load_image("icons/mail_tap_anywhere.png")

chief_order_img = load_image("icons/chief_order.png")
chief_order_productivity_day_img = load_image("icons/chief_order_productivity_day.png")
chief_order_urgent_mobilization_img = load_image("icons/chief_order_urgent_mobilization.png")
chief_order_rush_job_img = load_image("icons/chief_order_rush_job.png")
chief_order_festives_img = load_image("icons/chief_order_festives.png")
chief_order_back_img = load_image("icons/chief_order_back.png")
chief_order_enact_img = load_image("icons/chief_order_enact.png")

location_chat_img = load_image("icons/location_chat.png")
location_chat_exit_img = load_image("icons/location_chat_exit.png")
location_chief_order_img = load_image("icons/location_chief_order.png")
location_chief_profile_img = load_image("icons/location_chief_profile.png")
location_chief_profile_exit_img = load_image("icons/location_chief_profile_exit.png")
location_exploration_img = load_image("icons/location_exploration.png")
location_heroes_img = load_image("icons/location_heroes.png")
location_heroes_exit_img = load_image("icons/location_heroes_exit.png")
location_infantry_training_img = load_image("icons/location_infantry_training.png")
location_lancer_training_img = load_image("icons/location_lancer_training.png")
location_marksman_training_img = load_image("icons/location_marksman_training.png")
location_mail_img = load_image("icons/location_mail.png")
location_pet_img = load_image("icons/location_pet.png")
location_radar_img = load_image("icons/location_radar.png")
location_alliance_img = load_image("icons/location_alliance.png")

player_1_img = load_image("icons/player_1.png")
player_2_img = load_image("icons/player_2.png")
chief_profile_settings_img = load_image("icons/chief_profile_settings.png")
chief_profile_characters_img = load_image("icons/chief_profile_characters.png")
player_1_select_img = load_image("icons/player_1_select.png")
player_2_select_img = load_image("icons/player_2_select.png")
player_select_confirm_img = load_image("icons/player_select_confirm.png")

alliance_contribution_img = load_image("icons/alliance_contribution.png")
alliance_icon_img = load_image("icons/alliance_icon.png")
alliance_tech_img = load_image("icons/alliance_tech.png")
alliance_tech_recommended_img = load_image("icons/alliance_tech_recommended.png")
alliance_contribute_img = load_image("icons/alliance_contribute.png")
alliance_cannot_contribute_img = load_image("icons/alliance_cannot_contribute.png")
alliance_tech_close_img = load_image("icons/alliance_tech_close.png")
alliance_tech_back_img = load_image("icons/alliance_tech_back.png")

# Delay to allow switching to Bluestacks
time.sleep(wait_time)


'''
while True:
    click_help()
    time.sleep(wait_time)
    if find_and_click(heal_img, "   heal"):
        time.sleep(wait_time)
        find_and_click(help_img, "   help")
'''
#quick_healing()
'''
while True:
    radar()'''



#player_id=2

while True:
    reset_location()
    time.sleep(2*wait_time)
    click_help()
    time.sleep(wait_time)
    

    collect_exploration()
    time.sleep(wait_time)
    collect_rewards()
    time.sleep(wait_time)
    if (player_id == 1):
        train_infantry()
        time.sleep(wait_time)
        train_marksman()
        time.sleep(wait_time)
        train_lancers()
        time.sleep(wait_time)    
    
    recruitment() #free recruitment
    time.sleep(wait_time)

    read_mail()
    time.sleep(wait_time)
    chief_order()
    time.sleep(wait_time)
    alliance_tech()
    time.sleep(wait_time)

    find_and_click(world_img, "Switch to world", 0.7)
    time.sleep(4*wait_time)

    healing()#world
    time.sleep(wait_time)
    if not radar():#world
        reset_location()
    print(f"CURRENT PLAYER = {player_id}")
    time.sleep(5*wait_time)
    first_screen()
    if player_id==1:
        time.sleep(15*60)
    ''' if player_id == 2:
        gathering() # world
        time.sleep(wait_time)'''
