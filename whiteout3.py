import cv2
import numpy as np
import pyautogui
import time
import os
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pynput.mouse import Button, Controller
import math
import copy
import json

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

def find_image(images, debug_name="", threshold=0.8, important=False, cnt_tries=5):
    """Find the target image on screen using template matching and click it if found."""
    #print (f"find_image {debug_name} {important
    #print(f"images type={type(images)}")
    
    for i in range(cnt_tries):
    # Take a screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to OpenCV format
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        for image in images:
            #print(f"image type={type(image)}")
            # Perform template matching
            result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
            
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            
            # Print confidence score

            x, y = max_loc
            h, w = image.shape[:2]
            
            if debug>0 or important:
                t=str(int(max_val*100))
                if max_val >= threshold:
                    t=t+" OK"
            
                debug_screenshot = copy.deepcopy(screenshot)
                debug_screenshot[180:180+image.shape[0],0:image.shape[1]] = image
                debug_screenshot = cv2.putText(debug_screenshot, t, (0,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)#fit
            
                # Draw rectangle on matched area (for debugging)
                
                cv2.rectangle(debug_screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
                filename = f"debug/{timestamp}_{debug_name}.png"
                cv2.imwrite(filename, debug_screenshot)
        #        print(f"🔍 Debug image saved: {filename}")

            # If confidence is above threshold, click the image
            if max_val >= threshold:
                click_x, click_y = x + w // 2, y + h // 2


                return click_x, click_y
        
    return None, None

def find_image_new(images, debug_name="", threshold=0.8, important=False, cnt_tries=5):
    """Find the target image on screen using template matching and click it if found."""
    #print (f"find_image {debug_name} {important
    #print(f"images type={type(images)}")
    
    for i in range(cnt_tries):
    # Take a screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to OpenCV format
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        screenshotR, screenshotG, screenshotB = cv2.split(screenshot)
        for image in images:
            #print(f"image type={type(image)}")
            # Perform template matching
            imageR, imageG, imageB = cv2.split(image)
            resultR = cv2.matchTemplate(screenshotR, imageR, cv2.TM_CCOEFF_NORMED)
            resultG = cv2.matchTemplate(screenshotG, imageG, cv2.TM_CCOEFF_NORMED)
            resultB = cv2.matchTemplate(screenshotB, imageB, cv2.TM_CCOEFF_NORMED)
            
            #result is a table where value of x,y dimension defined probability
            result = resultR+resultG+resultB
            
            
            # Print confidence score

            loc = np.where(result>=3*threshold)
            #print(loc.shape)
            for pt in zip(*loc[::-1]):
                x = pt[0]
                y = pt[1]
                break
            w = image.shape[1]
            h = image.shape[0]
            
            if debug>0 or important:
                t=str(int(result[x,y]/3*100))
                if len(loc) > 0:
                    t=t+" OK"
            
                debug_screenshot = copy.deepcopy(screenshot)
                debug_screenshot[180:180+image.shape[0],0:image.shape[1]] = image
                debug_screenshot = cv2.putText(debug_screenshot, t, (0,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)#fit
            
                # Draw rectangle on matched area (for debugging)
                
                cv2.rectangle(debug_screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
                filename = f"debug/{timestamp}_{debug_name}.png"
                cv2.imwrite(filename, debug_screenshot)
        #        print(f"🔍 Debug image saved: {filename}")

            # If confidence is above threshold, click the image
            if len(loc) > 0:
                click_x, click_y = x + w // 2, y + h // 2


                return click_x, click_y
        
    return None, None

def find_and_click(image, debug_name="", threshold=0.7, important=False, cnt_tries=5):
    """Find the target image on screen using template matching and click it if found."""
    # Perform template matching
    print(f"{datetime.now()} {debug_name}")
    
    click_x, click_y = find_image(image, debug_name, threshold, important, cnt_tries)
    
    if click_x is not None:

        #print(f"✅ Target found at ({click_x}, {click_y}), clicking...")
        pyautogui.click(click_x, click_y)
        print("    ✅ Success")
        time.sleep(0.2*wait_time)
        return True
    else:
        print("    ❌ Target not found.")
        return False

def click_anywhere():
    find_and_click((click_anywhere_img,), "   Anywhere", 0.7, False, 20)
    
def collect_exploration():
    print(f"{datetime.now()}Collecting exploration")
    player_str = "player_id"+str(player_id)
    
    if find_and_click((exploration_img, exploration2_img), "   Exploration"):
        print("   Click Claim")
    
        if find_and_click((exploration_claim_img,), "   Claim in Exploration",  0.9, False, 5):
            time.sleep(wait_time)
            print("   Click Confirm Claim")
            if find_and_click((exploration_claim_confirm_img,), "   Confirm Claim in Exploration", 0.9, False, 5):
                
                print("   Click Anywhere")
                find_and_click((exploration_tap_anywhere_img,), "   Tap anywhere in Exploration", 0.9, False, 10)
                character_state[player_str]["exploration"] = datetime.now()
            
        print("   ❌ Click Exploration back")
        find_and_click((exploration_back_img,), "   Back in Exploration", 0.9, False, 5)

def click_help(with_reset=False):
    print("❌  Clicking help")

    find_and_click((help_hand_img,), "Help", 0.8, False, 2)
    if (with_reset):
        reset_location()

def collect_rewards():
    print(f"{datetime.now()} Collecting rewards")

    if find_and_click((left_bar_img, left_bar2_img), "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        if find_and_click((online_rewards_img,), "   online rewards in a bar", 0.9, False, 1):
            if find_and_click((online_reward_img,), "   online reward"):
                find_and_click((online_rewards_tap_img,), "   online reward tap")
        else: find_and_click((close_bar_img,), "   close bar", 0.5)

def train_troops(update_only=False):
    print(f"{datetime.now()}Train troops")
    any_change = True
    while any_change:
        any_change = False
        if find_and_click((left_bar_img, left_bar2_img), "   Left bar", 0.7):
            time.sleep(wait_time)
            swipe(915, 474, 915, 374)
            if find_and_click((marksman_completed_img, marksman_idle_img), "   marksman completed or idle in a bar", 0.9, False, 1):
                train_marksman(update_only)
                any_change = True
            elif find_and_click((infantry_completed_img, infantry_idle_img), "   infantry completed or idle in a bar", 0.9, False, 1):
                train_infantry(update_only)
                any_change = True
            elif find_and_click((lancers_completed_img, lancers_idle_img), "   lancers completed or idle in a bar", 0.9, False, 1):
                train_lancers(update_only)
                any_change = True
            else: 
                find_and_click((close_bar_img,), "   close bar", 0.5)

def train_execute(update_only=False):
    if find_and_click((train_img,), "   train click"):

        if find_and_click((troops_upgrade_img,), "   troops upgrade", 0.7, False, 10):
            find_and_click((troops_upgrade_confirm_img,), "   troops upgrade confirm")
            find_and_click((troops_promotion_img,), "   troops promotion")
        elif not update_only:
            find_and_click((train_button_img,), "   train button click")

        find_and_click((training_back_img,), "   training_back click")
    
        
def train_marksman(update_only=False):
    print(f"{datetime.now()} Train marksman")
            
    find_and_click((marksman_click_img,), "   marksman click", 0.7, False, 10)
    
    find_and_click((marksman_camp_click_img,), "   marksman camp click", 0.7, False, 10)

    train_execute()

def train_infantry(update_only=False):
    print(f"{datetime.now()} Train infantry")

    find_and_click((infantry_click_img,), "   infantry click")
    
    find_and_click((infantry_camp_img,), "   infantry camp click", 0.7, False, 10)
    
    train_execute()

def train_lancers(update_only = False):
    print(f"{datetime.now()} Train lancers")

    find_and_click((lancers_click_img,), "   lancers click")
    
    find_and_click((lancers_camp_img,), "   lancers camp click")
        
    train_execute()
    
def radar_attack():
    if (find_and_click((view_img,), "  view")):
        #time.sleep(wait_time)
        if (find_and_click((attack_img,), "  attack")):                        
            print("  attack")
            #time.sleep(wait_time)
            if (find_and_click((march_queue_img,), "  march queue")): # no troops
                        #time.sleep(wait_time)
                        find_and_click((march_queue_close_img,), "  march queue close")
                        return 1
            if (find_image((attack_likely_to_prevail_img, attack_risky_img), "  attack likely to prevail") != (None, None)): #not too strong opponent
                #time.sleep(wait_time)
                if (find_and_click((march_deploy_img,), "  deploy")):
                    #time.sleep(wait_time)
                    if (find_image((stamina_missing_img,), "   stamina_missing") != (None, None)):
                        #time.sleep(wait_time)
                        find_and_click((stamina_missing_close_img,), "   stamina_missing_close")
                        #time.sleep(wait_time)
                        find_and_click((exploration_back_img,), "   exploration_back")
                        return 3
            else:#too strong
                find_and_click((attack_back_img,), "  too strong - attack back")
                return 2
        else:
            #time.sleep(wait_time)
            if (find_and_click((march_queue_img,), "  march queue")): # no troops
                #time.sleep(wait_time)
                find_and_click((march_queue_close_img,), "  march queue close")
                return 1
    elif find_image((radar_marching_img,), "   marching"):
        (x,y) = find_image((radar_marching_img,), "   marching")
        if x != None:
            pyautogui.click(x, y+100)
    '''else: #it should never come here
        #time.sleep(wait_time)
        if (find_and_click((radar_tap_anywhere_img,), "  click anywhere", 0.5)):
            return 0
        else:
            return 4'''
    return 0
            
def radar(current_player_id):
    global character_state
    
    print(f"{datetime.now()} Radar")
 #   find_and_click(world_img, "   world", 0.7)
 #   time.sleep(2*wait_time)
    devil_visited = False
    player_str = "player_id"+str(current_player_id)
    
    if character_state[player_str].get("no troops", datetime(1900, 1,1)) > datetime.now() + timedelta(minutes=20):#not enough stamina or troops
        return True

    while True:
        if find_and_click((radar_img,location_radar_img), "  radar") :
            
            # if not in radar enter radar
            if find_image((location_radar_img,)," ...check location radar", 0.7, False, 10) == (None, None):
                find_and_click((radar_img,), "   radar")
            time.sleep(wait_time)
            if (not "radar_done" in character_state or character_state["radar_done"] > datetime.now() + timedelta(hours=8)) \
            or (not "radar_tent" in character_state[player_str] or character_state[player_str]["radar_tent"] > datetime.now() + timedelta(minutes=15)) \
            or (not "radar_swords" in character_state[player_str] or character_state[player_str]["radar_swords"] > datetime.now() + timedelta(hours=8)) \
            or (not "radar_skull" in character_state[player_str] or character_state[player_str]["radar_skull"] > datetime.now() + timedelta(hours=8)) \
            or (not "radar_devil" in character_state[player_str] or character_state[player_str]["radar_devil"] > datetime.now() + timedelta(days=1)):
                while find_and_click((radar_tent_gold_done_img, radar_tent_purple_done_img, radar_tent_blue_done_img, radar_swords_blue_done_img, radar_swords_purple_done_img, radar_swords_golden_done_img, radar_skull_blue_done_img, radar_skull_purple_done_img, radar_skull_golden_done_img, radar_devil_done_img), "  radar done", 0.9, False, 1):
                    print("   ->Done loop")
                    while find_and_click((radar_tap_anywhere_img,), "  click anywhere", 0.7, False, 5):
                        find_and_click((radar_tap_anywhere_img,), "  click anywhere", 0.7, False, 5)
                        
            character_state[player_str]["radar_done"]= datetime.now()
            if (not "radar_tent" in character_state[player_str] or character_state[player_str]["radar_tent"] > datetime.now() + timedelta(minutes=15)) and find_and_click((radar_tent_blue_img, radar_tent_gold_img, radar_tent_purple_img), "  radar tent", 0.9):
                
                find_and_click((radar_claim_img,), "  tent claim", 0.9, False, 5) #tent in progress and completed when on
                if (find_and_click((view_img,), "  view")): #normal tent to check
                    
                    find_and_click((radar_rescue_img,), "  tent rescue", 0.6, False, 5)
                    find_and_click((radar_claim_img,), "  tent claim", 0.9, False, 5)
                    
                    if (find_and_click((march_queue_img,), "  march queue")): # no troops
                        
                        find_and_click((march_queue_close_img,), "  march queue close")
                        break
                    if (find_image((stamina_missing_img,), "   stamina_missing") != (None, None)):#not enough stamina
                        
                        find_and_click((stamina_missing_close_img,), "   stamina_missing_close")
                        
                        find_and_click((exploration_back_img,), "   exploration_back", 0.9, False, 5)
                        break
                    #normal ending
                    character_state[player_str].pop("radar_done") #remove done flag, probably something done to collect
                else:
                    #time.sleep(wait_time)
                    if (find_and_click((radar_tap_anywhere_img,), "  click anywhere", 0.7)):#collect
                        break
            else:
                character_state[player_str]["radar_tent"]= datetime.now() #no tents
                if (not "radar_swords" in character_state[player_str] or character_state[player_str]["radar_swords"] > datetime.now() + timedelta(minutes=15)) \
                and find_and_click((radar_swords_blue_img, radar_swords_purple_img,radar_swords_golden_img), "  radar swords", 0.9, False, 5):
                    
                    
                    if (find_and_click((view_img,), "  view")):
                        
                        if (find_and_click((radar_explore_img,), "  explore")):
                            
                            if (find_and_click((fight_img,), "  fight"), 0.7, False, 30):#normal fight
                                
                                find_and_click((fight_tap_anywhere_img,), "  fight - tap anywhere", 0.7, False, 25)
                                #normal ending
                                character_state[player_str].pop("radar_done") #remove done flag, probably something done to collect
                            else: #stamina_missing
                                
                                if (find_image((stamina_missing_img,), "   stamina_missing") != (None, None)):
                                    #time.sleep(wait_time)
                                    find_and_click((stamina_missing_close_img,), "   stamina_missing_close")
                                    #time.sleep(wait_time)
                                    find_and_click((exploration_back_img,), "   exploration_back")
                                    break
                    else:
                        if find_and_click((radar_tap_anywhere_img,), "  click anywhere", 0.7):#collect
                            find_and_click((radar_exit_img,), "   radar exit", 0.9, False, 5)
                else:
                    character_state[player_str]["radar_swords"]= datetime.now()#no swords
                    if (not "radar_skull" in character_state[player_str] or character_state[player_str]["radar_skull"] > datetime.now() + timedelta(minutes=15)) \
                    and find_and_click((radar_skull_blue_img, radar_skull_purple_img, radar_skull_golden_img), "  radar skull", 0.9):
                        
                        if radar_attack() >0:#execute attack
                            break
                    else:
                        character_state[player_str]["radar_skull"]= datetime.now()#no skulls
                        if (not "radar_devil" in character_state or character_state["radar_devil"] > datetime.now() + timedelta(days=1)) and find_and_click((radar_devil_img,), "  radar devil"):
                            
                            ret = radar_attack()
                            if ret == 1 or ret == 3: # no troops available or no stamina
                                character_state[player_str]["no troops"]=datetime.now()
                                break
                            elif ret == 2:# too strong - TODO: it can be because main march is unavailable
                                character_state[player_str]["radar_devil"]= datetime.now()
                                devil_visited=True
                                break
                        else:
                            return False #nothing found
        else: #no radar
            return False #error
    
    find_and_click((radar_exit_img,), "  radar exit")

    return True #something found
    

def recruitment() :
    print(f"{datetime.now()} Recruitment")
    if find_and_click((left_bar_img, left_bar2_img), "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        if (find_and_click((recruitment_img,), "  recruitment", 0.9, False, 1)):
            #time.sleep(wait_time)
            find_and_click((recruit_free_img,), "  recruit free")
            #time.sleep(3*wait_time)
            find_and_click((recruit_tap_img,), "  recruit tap", 0.7, False, 15)
            #time.sleep(wait_time)
            find_and_click((radar_exit_img,), "  exit", 0.7, False, 5)
            find_and_click((radar_exit_img,), "  exit", 0.7, False, 5)
        else: find_and_click((close_bar_img,), "   close bar", 0.5)
            

def gathering() :
    print(f"{datetime.now()} Gathering")
#    find_and_click(world_img, "   world", 0.7)
#    time.sleep(4*wait_time)
    if find_and_click((map_search_img,), "   map search"):
       #time.sleep(wait_time)
       if find_and_click((map_iron_img,), "   map iron"):
           #time.sleep(wait_time)
           if find_and_click((search_img,), "   search"):
               #time.sleep(2*wait_time)
               find_and_click((gather_img,), "   gather", 0.7, False, 10)
               #time.sleep(wait_time)
               if (find_and_click((march_queue_img,), "  march queue")): # no troops
                   #time.sleep(wait_time)
                   find_and_click((march_queue_close_img,), "  march queue close")
                   return None
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((add_hero_img,), "   add hero")
               #time.sleep(wait_time)
               find_and_click((iron_hero_img,), "   iron hero")
               #time.sleep(wait_time)
               find_and_click((assign_img,), "   assign")
               #time.sleep(wait_time)
               find_and_click((assign_close_img,), "   assign close")
               #time.sleep(2*wait_time)
               find_and_click((gather_deploy_img,), "   deploy", 0.7, False, 10)
       #time.sleep(wait_time)
       if find_and_click((map_coal_img,), "   map coal"):
           #time.sleep(wait_time)
           if find_and_click((search_img,), "   search"):
               #time.sleep(2*wait_time)
               find_and_click((gather_img,), "   gather", 0.7, False, 10)
               #time.sleep(wait_time)
               if (find_and_click((march_queue_img,), "  march queue")): # no troops
                   #time.sleep(wait_time)
                   find_and_click((march_queue_close_img,), "  march queue close")
                   return None
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((add_hero_img,), "   add hero")
               #time.sleep(wait_time)
               #swipe(1015, 474, 1015, 374)
               find_and_click((coal_hero_img,), "   coal hero")
               #time.sleep(wait_time)
               find_and_click((assign_img,), "   assign")
               #time.sleep(wait_time)
               find_and_click((assign_close_img,), "   assign close")
               #time.sleep(2*wait_time)
               find_and_click((gather_deploy_img,), "   deploy", 0.7, False, 10)
       if find_and_click((map_wood_img,), "   map wood"):
           #time.sleep(wait_time)
           if find_and_click((search_img,), "   search"):
               #time.sleep(2*wait_time)
               find_and_click((gather_img,), "   gather", 0.7, False, 10)
               #time.sleep(wait_time)
               if (find_and_click((march_queue_img,), "  march queue")): # no troops
                   #time.sleep(wait_time)
                   find_and_click((march_queue_close_img,), "  march queue close")
                   return None
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((add_hero_img,), "   add hero")
               #time.sleep(wait_time)
               #swipe(1015, 474, 1015, 374)
               find_and_click((wood_hero_img,), "   wood hero")
               #time.sleep(wait_time)
               find_and_click((assign_img,), "   assign")
               #time.sleep(wait_time)
               find_and_click((assign_close_img,), "   assign close")
               #time.sleep(2*wait_time)
               find_and_click((gather_deploy_img,), "   deploy", 0.7, False, 10)
       
       if find_and_click((map_meat_img,), "   map meat"):
           #time.sleep(wait_time)
           if find_and_click((search_img,), "   search"):
               #time.sleep(2*wait_time)
               find_and_click((gather_img,), "   gather", 0.7, False, 10)
               #time.sleep(wait_time)
               if (find_and_click((march_queue_img,), "  march queue")): # no troops
                   #time.sleep(wait_time)
                   find_and_click((march_queue_close_img,), "  march queue close")
                   return None
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((remove_hero_img,), "   remove hero")
               #time.sleep(wait_time)
               find_and_click((add_hero_img,), "   add hero")
               #time.sleep(wait_time)
               #swipe(1015, 474, 1015, 374)
               find_and_click((meat_hero_img,), "   meat hero")
               #time.sleep(wait_time)
               find_and_click((assign_img,), "   assign")
               #time.sleep(wait_time)
               find_and_click((assign_close_img,), "   assign close")
               #time.sleep(2*wait_time)
               find_and_click((gather_deploy_img,), "   deploy", 0.7, False, 10)
       
def healing():
    print(f"{datetime.now()} Heal")
#    find_and_click(world_img, "   world", 0.7)
#    time.sleep(4*wait_time)
    if find_and_click((heal_icon_img,), "   heal icon"):
        #time.sleep(wait_time)
        if find_and_click((heal_img,), "   heal"):
            #time.sleep(wait_time)
            find_and_click((help_img,), "   help")
            click_help()
            #time.sleep(wait_time)
#    find_and_click(city_img, "   city", 0.7)
#    time.sleep(2*wait_time)

def quick_healing():
    print("Quick heal")
    if find_and_click((heal_icon_img,), "   heal icon"):
        while True:
            if find_and_click((heal_img,), "   heal"):
                #time.sleep(wait_time)
                find_and_click((help_img,), "   help")
                click_help()
                #time.sleep(wait_time)
            if find_image((location_chat_img,), "...chat location") != (None, None):
                find_and_click((location_chat_exit_img,), "...exit chat")
                #time.sleep(wait_time)
                find_and_click((heal_icon_img,), "   heal icon")

                    
def first_screen():
    print(f"{datetime.now()} First screen")
    while find_and_click((reconnect_img,), "   click reconnect"):
        if not find_image((reconnect_img,), "   image reconnect check"):
            break
        else:
            print("   CONNECTION LOST - waiting")
            time.sleep(10*wait_time)
    
    if find_and_click((add_cross_img, add_cross2_img, add_cross3_img, add_cross4_img, add_cross5_img), "...add cross", 0.8, False, 50)!= (None, None):
        find_and_click((confirm_img,), "  confirm", 0.7, False, 10)
        #time.sleep(wait_time)
    else:
        print("  no add?")
        
    find_and_click((reklamy_img,), "   advertisements", 0.7)

def read_mail():
    print(f"{datetime.now()} Mail")
    if find_and_click((mail_img,), "   mail"):
        #time.sleep(wait_time)
        find_image((location_mail_img,)," ...check location mail")
        find_and_click((mail_reports_img,), "    mail reports", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_read_all_img,), "    mail read all", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_tap_anywhere_img,), "    mail tap anywhere", 0.7)
        #time.sleep(wait_time)
        find_and_click((mail_system_img,), "    mail system", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_read_all_img,), "    mail read all", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_tap_anywhere_img,), "    mail tap anywhere", 0.7)
        #time.sleep(wait_time)
        find_and_click((mail_alliance_img,), "    mail alliance", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_read_all_img,), "    mail read all", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_tap_anywhere_img,), "    mail tap anywhere", 0.7)
        #time.sleep(wait_time)
        find_and_click((mail_wars_img,), "    mail wars", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_read_all_img,), "    mail read all", 0.85)
        #time.sleep(wait_time)
        find_and_click((mail_tap_anywhere_img,), "    mail tap anywhere", 0.7)
        #time.sleep(wait_time)
        find_and_click((mail_exit_img,), "    mail exit", 0.85)
        
def chief_order():
    print(f"{datetime.now()} Chief order")
    if find_and_click((chief_order_img,), "   chief_order"):
        #time.sleep(wait_time)
        
        if find_and_click((chief_order_rush_job_img,), "   rush job", 0.9):
            #time.sleep(wait_time)
            find_and_click((chief_order_enact_img,), "   enact", 0.9)
            #time.sleep(wait_time)
            find_and_click((chief_order_tap_img,), "   chief order tap", 0.9, False, 30)
        if find_and_click((chief_order_festives_img,), "   festives", 0.9):
            #time.sleep(wait_time)
            find_and_click((chief_order_enact_img,), "   enact", 0.9)
        if find_and_click((chief_order_productivity_day_img,), "   productivity day", 0.9):
            #time.sleep(wait_time)
            find_and_click((chief_order_enact_img,), "   enact", 0.9)
        if find_and_click((chief_order_urgent_mobilization_img,), "   urgent mobilization", 0.9):
            #time.sleep(wait_time)
            find_and_click((chief_order_enact_img,), "   enact", 0.9)
        #time.sleep(wait_time)
        find_and_click((chief_order_back_img,), "   back", 0.9)
        #time.sleep(wait_time)
        find_and_click((chief_order_back_img,), "   back", 0.9)
        
def reset_location():
    print(f"{datetime.now()} Reset location")
    while find_image((appointment_tap_img,), "   appointment tap") != (None, None):
        find_and_click((appointment_tap_img,), "   appointment tap")

    if find_image((world_img,), "   city location") != (None, None):
        return None
    while find_image((city_img,), "   world location") != (None, None):
        find_and_click((city_img,), "   exit world")
    while find_image((location_chat_img,), "...chat location") != (None, None):
        find_and_click((location_chat_exit_img,), "...exit chat")
    while find_image((location_radar_img,), "...radar location") != (None, None):
        find_and_click((radar_exit_img,), "...exit radar")
    while find_image((location_exploration_img,), "...exploration location") != (None, None):
        find_and_click((exploration_back_img,), "...exit exploration")
    while find_image((location_infantry_training_img, location_lancer_training_img, location_marksman_training_img), "...training location") != (None, None):
        find_and_click((training_back_img,), "...training radar")
    while find_image((location_alliance_img,), "...location_alliance") != (None, None):
        find_and_click((alliance_tech_back_img,), "...alliance_tech_back")
    while find_image((location_chief_profile_img,), "...location_chief_profile_img") != (None, None):
        find_and_click((location_chief_profile_exit_img,), "...location_chief_profile_exit_img")
    
        
def change_player(current_player_id):
    print(f"{datetime.now()} Change player")
    print(f"   current_id={current_player_id}")
    if current_player_id==1:#current player ID
        current_player = player_1_img
        target_player = player_2_img
    elif current_player_id==2:
        current_player = player_2_img
        target_player = player_1_img
    
    if find_and_click((current_player,), "   enter profile", 0.7,False):
        #time.sleep(wait_time)
        find_and_click((chief_profile_settings_img,), "   enter settings", 0.7, False, 10)
        #time.sleep(wait_time)
        find_and_click((chief_profile_characters_img,), "   enter characters", 0.7, False)
        #time.sleep(wait_time)
        if current_player_id==1:
            find_and_click((player_2_select_img,), "   select player 2", 0.7, False)
            #time.sleep(wait_time)
        elif current_player_id==2:
            find_and_click((player_1_select_img,), "   select player 1", 0.7, False)
            #time.sleep(wait_time)
        find_and_click((player_select_confirm_img,), "   confirm player")
        if current_player_id == 1:
            current_player_id=2
        elif current_player_id==2:
            current_player_id=1
        time.sleep(wait_time*5)
    
    print(f"   new current_id={current_player_id}")
    
    #exit()
    return current_player_id

def detect_player():
    print(f"{datetime.now()} detect_player")
    if find_image((player_1_img,), "....find player 1", 0.9, False, 5) != (None, None):
        return 1
    elif find_image((player_2_img,), "....find player 2", 0.9, False, 5) != (None, None):
        return 2
    else:
        return 0
        
def alliance_tech():
    print(f"{datetime.now()} Alliance tech")
    
    if find_and_click((left_bar_img, left_bar2_img), "   Left bar", 0.7):
        #time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        if find_and_click((alliance_contribution_img,), "   alliance_contribution", 0.7, False, 1):
            #time.sleep(wait_time)
            if not find_and_click((alliance_icon_img,), "   alliance_icon", 0.7, False, 10):
                return None
            
            if not find_and_click((alliance_tech_img,), "   alliance_tech", 0.7):
                return None
            #time.sleep(wait_time)
            if find_and_click((alliance_tech_recommended_img,), "   alliance_tech recommended", 0.7):
                #time.sleep(wait_time)
                try_number=1
                while find_image((alliance_cannot_contribute_img,), "   alliance cannot contribute")==(None, None) and try_number<=25:
                    find_and_click((alliance_contribute_img,), "   alliance_contribute", 0.7)
                    #time.sleep(wait_time)
                    try_number=try_number+1
                find_and_click((alliance_tech_close_img,), "   alliance_tech close", 0.7)
                #time.sleep(wait_time)
                find_and_click((alliance_tech_back_img,), "   alliance_tech back", 0.7)
                #time.sleep(wait_time)
                find_and_click((alliance_chests_img,), "   alliance chests",0.7)
                if find_and_click((alliance_chests_big_img,), "   alliance chests big",0.7):
                    find_and_click((alliance_chests_tap_img,), "   alliance chests tap",0.7)
                if find_and_click((alliance_chests_gift_claim_all_img,), "   alliance chests gift claim all",0.7):
                    find_and_click((alliance_chests_tap_img,), "   alliance chests tap",0.7)
                if find_and_click((alliance_chests_loot_img,), "   alliance chests loot",0.7):
                    if find_and_click((alliance_chests_claim_all_img,), "   alliance chests claim all",0.7):
                        find_and_click((alliance_chests_tap_img,), "   alliance chests tap",0.7)
            find_and_click((alliance_tech_back_img,), "   alliance_tech back", 0.7)
            find_and_click((alliance_tech_back_img,), "   alliance_tech back", 0.7)
            #time.sleep(wait_time)
            
def daily_missions():
    print(f"{datetime.now()} Daily missions")
    if find_and_click((daily_missions_img,), "   daily missions", 0.7):
        if find_and_click((daily_missions_claim_all_img,), "   daily mission claim all", 0.7):
            find_and_click((daily_missions_tap_img,), "   daily missions tap", 0.7)
            find_and_click((daily_missions_tap_img,), "   daily missions tap", 0.7)
        find_and_click((daily_missions_exit_img,), "   daily missions exit", 0.7)
        
def backpack():
    print(f"{datetime.now()} Backpack")
    if find_and_click((backpack_img,), "   backpack"):
        any_change=True
        time.sleep(wait_time)
        while any_change:
            any_change=False
            if find_and_click((backpack_diamonds_1k_img, backpack_diamonds_1_img, backpack_diamonds_10_img, backpack_diamonds_100_img, backpack_exp_1k_img, backpack_exp_5k_img, backpack_exp_10k_img, backpack_exp_50k_img), "   backpack resources", 0.7, False):
                any_change=True
                find_and_click((backpack_use_img,), "   backpack use", 0.7, False, 10)
                
        find_and_click((backpack_speedups_img,), "   backpack speedups")
        find_and_click((backpack_bonus_img,), "   backpack bonus")
        find_and_click((backpack_gear_img,), "   backpack gear")
        find_and_click((backpack_other_img,), "   backpack other")
        find_and_click((alliance_tech_back_img,), "   backpack exit")

def tree_of_life():
    print(f"{datetime.now()} Tree of life")
    if find_and_click((left_bar_img, left_bar2_img), "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        cnt_tries=0
        if find_and_click((tree_img,), "   tree left bar", 0.7, False):
            while find_and_click((tree_collect_img, ),"   tree collect", 0.6, False, 20) and cnt_tries<max_tries:
                time.sleep(0.2*wait_time)
                cnt_tries=cnt_tries+1
            find_and_click((tree_exit_img,),"   tree exit", 0.7, False, 20)

def pet_adventure():
    print(f"{datetime.now()} Pet adventure")
    if find_and_click((left_bar_img, left_bar2_img), "   Left bar", 0.7):
        time.sleep(wait_time)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        swipe(915, 474, 915, 374)
        time.sleep(wait_time)
        if find_and_click((pet_adventure_ready_img, pet_adventure_completed_img), "   pet adventure ready left bar", 0.7, False):
            while find_and_click((pet_adventure_medium_done_img, pet_adventure_low_done_img), "   pet adventure done", 0.7, False):
                find_and_click((pet_adventure_done_collect_img,), "   pet adventure collect", 0.7, False, 20)
                while find_and_click((pet_adventure_collect_tap_img,), "   pet adventure collect tap", 0.7, False, 30):
                    time.sleep(wait_time*0.2)
            if find_and_click((pet_adventure_ally_img,), "   pet adventure ally", 0.7, False):
                find_and_click((pet_adventure_ally_collect_all_img,), "   pet adventure ally collect all", 0.7, False)
                find_and_click((pet_adventure_ally_collect_tap_img,), "   pet adventure ally collect tapo", 0.7, False, 20)
                find_and_click((pet_adventure_ally_collect_exit_img,), "   pet adventure ally collect exit", 0.7, False, 20)
            for i in range(3):
                if find_and_click((pet_adventure_high_img, pet_adventure_medium_img, pet_adventure_low_img,), "  pet adventure chest", 0.7, False):
                    if find_and_click((pet_adventure_select_pet_img,), "   select pet", 0.7, False):
                        find_and_click((pet_adventure_start_img,), "   pet adventure start", 0.7, False)
                    while find_and_click((pet_adventure_start_exit_img,), "   pet adventure start exit", 0.7, False, 20):
                         find_and_click((pet_adventure_start_exit_img,), "   pet adventure start exit", 0.7, False, 20)
            while find_and_click((pet_adventure_exit_img,), "   pet adventure  exit", 0.7, False, 20):
                 find_and_click((pet_adventure_exit_img,), "   pet adventure  exit", 0.7, False, 20)
        

def start_of_day():
    print(f"{datetime.now()} Start of day")
    if find_and_click((vip_img,), "   VIP", 0.7):
        if find_and_click((vip_claim_img,), "   VIP claim", 0.7):
            find_and_click((vip_claim_tap_img,), "   VIP claim tap", 0.7, False, 10)
        if find_and_click((vip_chest_img,vip_chest_2_img), "   VIP chest", 0.7):
            find_and_click((vip_chest_tap_img,), "   VIP chest tap", 0.7, False, 10)
        if find_and_click((vip_plus_img,), "   VIP plus", 0.9):
            while find_and_click((vip_plus_use_img,), "   VIP plus use", 0.7):
                find_and_click((vip_plus_use_img,), "   VIP plus use", 0.7)
            while find_and_click((vip_plus_exit_img,), "   VIP plus exit", 0.7):
                find_and_click((vip_plus_exit_img,), "   VIP plus exit", 0.7)
        while find_and_click((vip_exit_img,), "   VIP exit", 0.7):
             find_and_click((vip_exit_img,), "   VIP exit", 0.7)
        
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type is nor seralizable")        
  
print("Loading icon files...")
help_hand_img = load_image ("icons/help_hand.png")
recall_troops_img = load_image ("icons/recall_troops.png")
world_img = load_image ("icons/world.png")
city_img = load_image ("icons/city.png")

add_cross_img = load_image ("icons/add_cross.png")
add_cross2_img = load_image ("icons/add_cross2.png")
add_cross3_img = load_image ("icons/add_cross3.png")
add_cross4_img = load_image ("icons/add_cross4.png")
add_cross5_img = load_image ("icons/add_cross5.png")
exploration_img = load_image ("icons/exploration.png")
exploration2_img = load_image ("icons/exploration2.png")
click_anywhere_img = load_image ("icons/click_anywhere.png")

exploration_claim_img = load_image ("icons/exploration_claim.png")
exploration_claim_confirm_img = load_image ("icons/exploration_claim_confirm.png")
exploration_back_img = load_image ("icons/exploration_back.png")
exploration_tap_anywhere_img = load_image ("icons/exploration_tap_anywhere.png")
left_bar_img = load_image ("icons/left_bar.png")
left_bar2_img = load_image ("icons/left_bar2.png")
online_rewards_img = load_image ("icons/online_rewards.png")
online_reward_img = load_image ("icons/online_reward.png")
online_rewards_tap_img = load_image ("icons/online_rewards_tap.png")
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
radar_devil_done_img = load_image ("icons/radar_devil_done.png")
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
radar_tent_blue_done_img = load_image ("icons/tent_blue_done.png")
radar_tent_gold_img = load_image ("icons/tent_gold.png")
radar_tent_gold_done_img = load_image ("icons/tent_gold_done.png")
radar_tent_purple_img = load_image ("icons/tent_purple.png")
radar_tent_purple_done_img = load_image ("icons/tent_purple_done.png")

radar_skull_blue_img = load_image ("icons/skull_blue.png")
radar_skull_purple_img = load_image ("icons/skull_purple.png")
radar_skull_golden_img = load_image ("icons/skull_golden.png")
radar_skull_blue_done_img = load_image ("icons/skull_blue_done.png")
radar_skull_purple_done_img = load_image ("icons/skull_purple_done.png")
radar_skull_golden_done_img = load_image ("icons/skull_golden_done.png")


radar_swords_blue_img = load_image ("icons/swords_blue.png")
radar_swords_blue_done_img = load_image ("icons/swords_blue_done.png")
radar_swords_purple_img = load_image ("icons/swords_purple.png")
radar_swords_purple_done_img = load_image ("icons/swords_purple_done.png")
radar_swords_golden_img = load_image ("icons/swords_golden.png")
radar_swords_golden_done_img = load_image ("icons/swords_golden_done.png")


radar_rescue_img = load_image ("icons/tent_rescue.png")
radar_explore_img = load_image ("icons/radar_explore.png")
fight_img = load_image ("icons/fight.png")
radar_tap_anywhere_img = load_image ("icons/radar_tap_anywhere.png")
fight_tap_anywhere_img = load_image ("icons/fight_tap_anywhere.png")
stamina_missing_img = load_image ("icons/stamina_missing.png")
stamina_missing_close_img = load_image ("icons/stamina_missing_close.png")
radar_claim_img = load_image ("icons/radar_claim.png")
radar_marching_img = load_image ("icons/radar_marching.png")


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
chief_order_tap_img = load_image("icons/chief_order_tap.png")

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
alliance_chests_img = load_image("icons/alliance_chests.png")
alliance_chests_big_img = load_image("icons/alliance_chests_big.png")
alliance_chests_claim_all_img = load_image("icons/alliance_chests_claim_all.png")
alliance_chests_gift_claim_all_img = load_image("icons/alliance_chests_gift_claim_all.png")
alliance_chests_loot_img = load_image("icons/alliance_chests_loot.png")
alliance_chests_tap_img = load_image("icons/alliance_chests_tap.png")

daily_missions_img = load_image("icons/daily_missions.png")
daily_missions_claim_all_img = load_image("icons/daily_missions_claim_all.png")
daily_missions_tap_img = load_image("icons/daily_missions_tap.png")
daily_missions_exit_img = load_image("icons/daily_missions_exit.png")

backpack_img = load_image("icons/backpack.png")
backpack_use_img = load_image("icons/backpack_use.png")
backpack_diamonds_10_img = load_image("icons/backpack_diamonds_10.png")
backpack_diamonds_100_img = load_image("icons/backpack_diamonds_100.png")
backpack_diamonds_1_img = load_image("icons/backpack_diamonds_1.png")
backpack_diamonds_1k_img = load_image("icons/backpack_diamonds_1k.png")
backpack_exp_1k_img = load_image("icons/backpack_exp_1k.png")
backpack_exp_5k_img = load_image("icons/backpack_exp_5k.png")
backpack_exp_10k_img = load_image("icons/backpack_exp_10k.png")
backpack_exp_50k_img = load_image("icons/backpack_exp_50k.png")
backpack_speedups_img = load_image("icons/backpack_speedups.png")
backpack_bonus_img = load_image("icons/backpack_bonus.png")
backpack_gear_img = load_image("icons/backpack_gear.png")
backpack_other_img = load_image("icons/backpack_other.png")

tree_img = load_image("icons/tree_of_life.png")
tree_collect_img = load_image("icons/tree_of_life_collect.png")
tree_collect_HQ_img = load_image("icons/tree_of_life_collect_HQ.png")
tree_exit_img = load_image("icons/tree_of_life_exit.png")

appointment_tap_img = load_image("icons/appointment_tap.png")

pet_adventure_ready_img = load_image("icons/pet_adventure_ready.png")
pet_adventure_ally_img = load_image("icons/pet_adventure_ally.png")
pet_adventure_ally_collect_all_img = load_image("icons/pet_adventure_ally_collect_all.png")
pet_adventure_ally_collect_tap_img = load_image("icons/pet_adventure_ally_collect_tap.png")
pet_adventure_ally_collect_exit_img = load_image("icons/pet_adventure_ally_collect_exit.png")
pet_adventure_low_img = load_image("icons/pet_adventure_low.png")
pet_adventure_low_done_img = load_image("icons/pet_adventure_low_done.png")
pet_adventure_medium_img = load_image("icons/pet_adventure_medium.png")
pet_adventure_medium_done_img = load_image("icons/pet_adventure_medium_done.png")
pet_adventure_high_img = load_image("icons/pet_adventure_high.png")
pet_adventure_select_pet_img = load_image("icons/pet_adventure_select_pet.png")
pet_adventure_start_img = load_image("icons/pet_adventure_start.png")
pet_adventure_start_exit_img = load_image("icons/pet_adventure_start_exit.png")
pet_adventure_exit_img = load_image("icons/pet_adventure_exit.png")
pet_adventure_completed_img = load_image("icons/pet_adventure_completed.png")
pet_adventure_done_collect_img = load_image("icons/pet_adventure_done_collect.png")
pet_adventure_collect_tap_img = load_image("icons/pet_adventure_collect_tap.png")

vip_img = load_image("icons/vip.png")
vip_claim_img = load_image("icons/vip_claim.png")
vip_claim_tap_img = load_image("icons/vip_claim_tap.png")
vip_chest_img = load_image("icons/vip_chest.png")
vip_chest_2_img = load_image("icons/vip_chest_2.png")
vip_chest_tap_img = load_image("icons/vip_chest_tap.png")
vip_plus_img = load_image("icons/vip_plus.png")
vip_plus_use_img = load_image("icons/vip_plus_use.png")
vip_plus_exit_img = load_image("icons/vip_plus_exit.png")
vip_exit_img = load_image("icons/vip_exit.png")
print("Loading icon files...COMPLETED")
# Delay to allow switching to Bluestacks
time.sleep(wait_time)

#quick_healing()



#debug=1


#start_of_day()
#tree_of_life()
#debug=0

#pet_adventure()
#first_screen()
#exit()



player_id=detect_player()

if (player_id == 0):
    print("ERROR: Cannot identify player!!!")
    exit()
    
try:
    with open('whiteout.json') as file:
        character_state=json.load(file)
        

except (IOError) as e:
    print(f"Error loading data: {e}")
    character_state={"player_id1":{"player_id":1}, "player_id2":{"player_id":2}}
    
#debug=1
#radar(2)
#exit()
#first_screen()
while True:
#if True:

    #reset_location()
    click_help(True) #help with reset
    time.sleep(2*wait_time)
    
    print(character_state)
    #get stamina
    print(f"   current_id={player_id}")
    tree_of_life()
    time.sleep(wait_time)
    backpack()
    
    time.sleep(wait_time)
    

    collect_exploration()
    time.sleep(wait_time)
    collect_rewards()
    time.sleep(wait_time)
    #if (player_id == 1):
    train_troops(False)
    #elif (player_id == 2):
    #    train_troops(True)
    recruitment() #free recruitment
    time.sleep(wait_time)

    read_mail()
    time.sleep(wait_time)
    chief_order()
    time.sleep(wait_time)
    alliance_tech()
    time.sleep(wait_time)

    daily_missions()
    time.sleep(wait_time)
    pet_adventure()

    try_number=1
    while find_image((city_img,),"   world check") == (None, None) and try_number<max_tries:
        find_and_click((world_img,), "Switch to world", 0.7)
        time.sleep(4*wait_time)
        try_number=try_number+1

    healing()#world
    time.sleep(wait_time)
    
    if not radar(player_id):#world
        reset_location()
    try:
        with open('whiteout.json', 'w') as file:
            json_string = json.dumps(character_state, default=serialize_datetime, indent=4)
            file.write(json_string)
    except (IOError) as e:
        print(f"Error saving data: {e}")

    reset_location()
    '''if player_id == 2:
        gathering() # world
        time.sleep(wait_time)
        time.sleep(wait_time)'''

    '''player_id = change_player(player_id)
    print(f"CURRENT PLAYER = {player_id}")'''
    time.sleep(5*wait_time)
    first_screen()
    #if player_id==1:
    time.sleep(1*60)

