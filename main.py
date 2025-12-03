import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Key mappings for directions - SETAS DO TECLADO
KEY_UP = 'w'
KEY_DOWN = 's'
KEY_LEFT = 'a'
KEY_RIGHT = 'd'
KEY_ACTION = 'z'
KEY_ACTION2 = 'x' 

KEY_UP1 = 'up'
KEY_DOWN2 = 'down'
KEY_LEFT3 = 'left'
KEY_RIGHT4 = 'right'


# Cooldown para inputs contínuos
continuous_cooldown = 0.15
fist_cooldown = 0.3
single_finger_cooldown = 0.3  # Cooldown para o novo botão

# Box settings
box_width = 120
box_height = 80

# Estado das caixas e punho
current_box = None
last_continuous_time = 0
fist_active = False
last_fist_time = 0
single_finger_active = False  # Estado para o novo botão
last_single_finger_time = 0.1  # Timer para o novo botão

# Para controlar teclas pressionadas
active_keys = set()

cap = cv2.VideoCapture(0)

def is_fist_closed(hand_landmarks):
    """Detecta se a mão está fechada (punho)"""
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]
    
    thumb_mcp = hand_landmarks.landmark[2]
    index_mcp = hand_landmarks.landmark[5]
    middle_mcp = hand_landmarks.landmark[9]
    ring_mcp = hand_landmarks.landmark[13]
    pinky_mcp = hand_landmarks.landmark[17]
    
    fingers_closed = 0
    
    if thumb_tip.y > thumb_mcp.y:
        fingers_closed += 1
    if index_tip.y > index_mcp.y:
        fingers_closed += 1
    if middle_tip.y > middle_mcp.y:
        fingers_closed += 1
    if ring_tip.y > ring_mcp.y:
        fingers_closed += 1
    if pinky_tip.y > pinky_mcp.y:
        fingers_closed += 1
    
    return fingers_closed >= 4

def is_single_finger_up(hand_landmarks):
    """Detecta se apenas um dedo está levantado (indicador)"""
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]
    
    thumb_mcp = hand_landmarks.landmark[2]
    index_mcp = hand_landmarks.landmark[5]
    middle_mcp = hand_landmarks.landmark[9]
    ring_mcp = hand_landmarks.landmark[13]
    pinky_mcp = hand_landmarks.landmark[17]
    
    # Verifica quantos dedos estão levantados
    fingers_up = 0
    
    # Polegar - lógica diferente devido à anatomia
    if thumb_tip.x < thumb_mcp.x:  # Para mão direita, polegar para esquerda significa levantado
        fingers_up += 1
    
    # Dedo indicador
    if index_tip.y < index_mcp.y:
        fingers_up += 1
    
    # Dedo médio
    if middle_tip.y < middle_mcp.y:
        fingers_up += 1
    
    # Dedo anelar
    if ring_tip.y < ring_mcp.y:
        fingers_up += 1
    
    # Dedo mindinho
    if pinky_tip.y < pinky_mcp.y:
        fingers_up += 1
    
    # Retorna True se APENAS o dedo indicador estiver levantado
    # (1 dedo levantado no total)
    return fingers_up == 1

def release_all_keys():
    """Libera todas as teclas pressionadas"""
    global active_keys
    for key in list(active_keys):
        pyautogui.keyUp(key)
        active_keys.remove(key)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_height, frame_width = frame.shape[:2]
    
    boxes = [
        (frame_width // 2 - box_width // 2, 0, frame_width // 2 + box_width // 2, box_height, KEY_UP, "Cima", (0, 255, 0)),
        (frame_width // 2 - box_width // 2, frame_height - box_height, frame_width // 2 + box_width // 2, frame_height, KEY_DOWN, "Baixo", (0, 0, 255)),
        (0, frame_height // 2 - box_height // 2, box_width, frame_height // 2 + box_height // 2, KEY_LEFT, "Esquerda", (255, 0, 0)),
        (frame_width - box_width, frame_height // 2 - box_height // 2, frame_width, frame_height // 2 + box_height // 2, KEY_RIGHT, "Direita", (0, 255, 255))
    ]
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_wrist_x = None
    current_wrist_y = None
    fist_detected = False
    single_finger_detected = False  # Nova variável para detecção
    new_box = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            current_wrist_x = hand_landmarks.landmark[0].x
            current_wrist_y = hand_landmarks.landmark[0].y
            
            wrist_x_pixel = int(current_wrist_x * frame_width)
            wrist_y_pixel = int(current_wrist_y * frame_height)
            
            cv2.circle(frame, (wrist_x_pixel, wrist_y_pixel), 10, (0, 255, 0), -1)
            
            # Detecção do punho (botão Z)
            if is_fist_closed(hand_landmarks):
                fist_detected = True
                cv2.circle(frame, (wrist_x_pixel, wrist_y_pixel), 15, (0, 0, 255), 3)
                cv2.putText(frame, "Botao Z", (wrist_x_pixel - 30, wrist_y_pixel - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                if not fist_active and time.time() - last_fist_time > fist_cooldown:
                    pyautogui.press(KEY_ACTION)
                    cv2.putText(frame, "Z", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                    fist_active = True
                    last_fist_time = time.time()
            
            # Detecção de apenas um dedo levantado (botão X)
            if is_single_finger_up(hand_landmarks):
                single_finger_detected = True
                cv2.circle(frame, (wrist_x_pixel, wrist_y_pixel), 12, (255, 0, 255), 3)
                cv2.putText(frame, "Botao X", (wrist_x_pixel - 30, wrist_y_pixel - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
                
                if not single_finger_active and time.time() - last_single_finger_time > single_finger_cooldown:
                    pyautogui.press(KEY_ACTION2)
                    cv2.putText(frame, "X", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 255), 2)
                    single_finger_active = True
                    last_single_finger_time = time.time()
            
            # Só verifica as caixas de direção se não estiver detectando gestos de ação
            if not fist_detected and not single_finger_detected:
                for box in boxes:
                    x1, y1, x2, y2, key, label, color = box
                    if (x1 <= wrist_x_pixel <= x2 and y1 <= wrist_y_pixel <= y2):
                        new_box = (key, label, color)
                        break

    current_time = time.time()
    
    # Libera teclas anteriores se mudou de caixa
    if current_box != new_box and current_box is not None:
        pyautogui.keyUp(current_box[0])
        if current_box[0] in active_keys:
            active_keys.remove(current_box[0])
    
    if new_box is not None:
        if current_box != new_box:
            current_box = new_box
            last_continuous_time = current_time
            # Pressiona a nova tecla
            pyautogui.keyDown(new_box[0])
            active_keys.add(new_box[0])
            cv2.putText(frame, f"Continuo: {new_box[1]}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, new_box[2], 2)
        
        elif current_time - last_continuous_time > continuous_cooldown:
            # Mantém a tecla pressionada
            if new_box[0] not in active_keys:
                pyautogui.keyDown(new_box[0])
                active_keys.add(new_box[0])
            last_continuous_time = current_time
            cv2.putText(frame, f"Continuo: {new_box[1]}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, new_box[2], 2)
    
    else:
        if current_box is not None:
            pyautogui.keyUp(current_box[0])
            if current_box[0] in active_keys:
                active_keys.remove(current_box[0])
        current_box = None
    
    # Reseta estados dos botões de ação
    if not fist_detected:
        fist_active = False
    
    if not single_finger_detected:
        single_finger_active = False

    # Draw boxes
    for box in boxes:
        x1, y1, x2, y2, key, label, color = box
        thickness = 4 if current_box and current_box[1] == label else 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(frame, label, (x1 + 10, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow('Hand Movement Control', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# Libera todas as teclas ao sair
release_all_keys()
cap.release()
cv2.destroyAllWindows()