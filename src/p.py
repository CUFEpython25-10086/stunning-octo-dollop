"""
stringless_guitar.py
简单的“无弦吉他”原型（鼠标实时控制音高与音色，带拨弦力度）
依赖: numpy, sounddevice, pygame
"""

import numpy as np
import sounddevice as sd
import pygame
import threading
import time
from collections import deque

# -----------------------
# 配置参数
# -----------------------
SAMPLE_RATE = 48000
BUFFER_SIZE = 512  # 输出回调块大小（可调）
MAX_VOICES = 8

# 基本频率映射：屏幕 x -> MIDI note range
MIN_MIDI = 40   # E2-ish
MAX_MIDI = 88   # E6-ish

# 合成参数
WAVEFORM = 'saw'  # 'sine','saw','square'
MASTER_GAIN = 0.12

# -----------------------
# 共享状态（线程安全）
# -----------------------
state_lock = threading.Lock()

class Voice:
    def __init__(self, freq, vel=1.0):
        self.freq = float(freq)
        self.phase = 0.0
        self.amp = float(vel)
        self.env_state = 'attack'  # 'attack','sustain','release','off'
        self.env_time = 0.0
        self.release_time = None
        # envelope params (seconds)
        self.a = 0.005
        self.d = 0.05
        self.s = 0.7
        self.r = 0.25

    def trigger_release(self):
        if self.env_state != 'release':
            self.env_state = 'release'
            self.release_time = self.env_time

    def is_alive(self):
        return self.env_state != 'off'

    def envelope(self, dt):
        # simple ADSR step
        self.env_time += dt
        t = self.env_time
        if self.env_state == 'attack':
            if t < self.a:
                return (t / self.a)
            else:
                self.env_state = 'sustain'
                self.env_time = 0.0
                return self.s
        elif self.env_state == 'sustain':
            # sustain level
            return self.s
        elif self.env_state == 'release':
            # t counts since release
            if t < self.r:
                return self.s * (1.0 - (t / self.r))
            else:
                self.env_state = 'off'
                return 0.0
        else:
            return 0.0

voices = []

# global control parameters (updated by GUI)
control = {
    'mouse_pressed': False,
    'mouse_x': 0,
    'mouse_y': 0,
    'last_mouse_x': 0,
    'last_time': time.time(),
    'timbre': 0.5,
    'glide': True,
    'pitch_bend': 0.0,  # cents
}

# -----------------------
# 合成函数
# -----------------------
def midi_to_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def waveform_sample(wave, phase):
    # phase in [0,1)
    if wave == 'sine':
        return np.sin(2 * np.pi * phase)
    elif wave == 'saw':
        # naive saw
        return 2.0 * (phase - np.floor(phase + 0.5))
    elif wave == 'square':
        return 1.0 if phase < 0.5 else -1.0
    else:
        return np.sin(2 * np.pi * phase)

def add_voice(freq, vel=1.0):
    with state_lock:
        # 先清理已经死亡的voices
        voices[:] = [v for v in voices if v.is_alive()]
        
        if len(voices) >= MAX_VOICES:
            # 如果仍然超过限制，移除最老的voice
            voices.pop(0)
        
        voices.append(Voice(freq, vel))

def release_all_voices():
    with state_lock:
        for v in voices:
            v.trigger_release()

def audio_callback(outdata, frames, time_info, status):
    if status:
        print(f"Audio callback status: {status}")
    
    dt = 1.0 / SAMPLE_RATE
    buffer = np.zeros(frames, dtype=np.float32)
    
    # 快速获取需要的数据，尽量减少锁持有时间
    with state_lock:
        local_voices = [v for v in voices if v.is_alive()]  # 只复制存活的voices
        pitch_bend = control['pitch_bend']
        timbre = control['timbre']
    
    if len(local_voices) == 0:
        outdata[:] = (buffer.reshape(-1,1) * MASTER_GAIN)
        return

    # 处理音频生成
    for i in range(frames):
        s = 0.0
        for v in local_voices:
            # compute instantaneous frequency
            freq = v.freq * (2 ** (pitch_bend / 1200.0))
            phase_inc = freq * dt
            v.phase = (v.phase + phase_inc) % 1.0
            base = waveform_sample(WAVEFORM, v.phase)
            env = v.envelope(dt)
            # simple lowpass-like timbre control: mix saw/sine
            if WAVEFORM == 'saw':
                # mix with sine according to timbre param
                mix = (1.0 - timbre) * base + timbre * np.sin(2*np.pi*v.phase)
            else:
                mix = base
            s += mix * (v.amp * env)
        buffer[i] = s
    
    # 归一化处理
    max_val = np.max(np.abs(buffer))
    if max_val > 1e-6:
        buffer = buffer / max(1.0, max_val)
    
    outdata[:] = (MASTER_GAIN * buffer.reshape(-1,1)).astype(np.float32)

# -----------------------
# 启动音频流（非阻塞）
# -----------------------
stream = None
try:
    stream = sd.OutputStream(channels=1, callback=audio_callback,
                             samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE)
    stream.start()
    print("音频流启动成功")
except Exception as e:
    print(f"音频流启动失败: {e}")
    print("程序将以静音模式运行")

# -----------------------
# GUI 部分 (pygame)
# -----------------------
try:
    pygame.init()
    WIDTH, HEIGHT = 1100, 300
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("无弦吉他 原型 — 按住鼠标并移动以演奏")
    font = pygame.font.SysFont("Arial", 16)
    clock = pygame.time.Clock()
    print("Pygame窗口初始化成功")
except Exception as e:
    print(f"Pygame初始化失败: {e}")
    running = False

def x_to_midi(x):
    # map screen x to MIDI note range
    frac = np.clip(x / WIDTH, 0.0, 1.0)
    midi = MIN_MIDI + frac * (MAX_MIDI - MIN_MIDI)
    return midi

def draw_ui():
    try:
        screen.fill((20,20,20))
        # draw fretboard background
        pygame.draw.rect(screen, (35,35,35), (50, 50, WIDTH-100, HEIGHT-120), border_radius=8)
        # draw markers
        for i in range(0, 11):
            xi = 50 + (WIDTH-100) * (i / 10.0)
            pygame.draw.line(screen, (70,70,70), (xi, 50), (xi, 50+HEIGHT-120), 1)
        # draw current position
        with state_lock:
            mx = control['mouse_x']
            my = control['mouse_y']
            pressed = control['mouse_pressed']
            timbre = control['timbre']
        if pressed:
            pygame.draw.circle(screen, (255, 180, 60), (int(mx), int(my)), 14)
        else:
            pygame.draw.circle(screen, (180,180,180), (int(mx), int(my)), 8, 2)
        # show info text
        midi = x_to_midi(mx)
        freq = midi_to_freq(midi)
        txt_lines = [
            f"频率: {freq:.2f} Hz",
            f"MIDI: {midi:.2f}",
            f"音色(timbre): {timbre:.2f}",
            f"正在发声数: {len(voices)}",
            "操作：鼠标按住并移动—滑音；快速拖动并松开模拟拨弦；空格释放所有音"
        ]
        for i, line in enumerate(txt_lines):
            surf = font.render(line, True, (220,220,220))
            screen.blit(surf, (60, HEIGHT-40 + i*18))
        pygame.display.flip()
    except Exception as e:
        print(f"绘制UI时出错: {e}")

# -----------------------
# 主循环：处理事件并控制合成参数
# -----------------------
running = True
last_play_time = 0.0
frame_count = 0

try:
    while running:
        frame_count += 1
        if frame_count % 60 == 0:  # 每60帧打印一次状态
            print(f"主循环运行中... 帧数: {frame_count}")
        
        now = time.time()
        dt = now - control['last_time']
        control['last_time'] = now
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                with state_lock:
                    control['mouse_pressed'] = True
                    control['mouse_x'] = x
                    control['mouse_y'] = y
                    control['last_mouse_x'] = x
                # add voice
                midi = x_to_midi(x)
                freq = midi_to_freq(midi)
                # velocity based on vertical position (higher = stronger)
                vel = 1.0 - (y / HEIGHT)
                add_voice(freq, vel=vel)
                last_play_time = now
            elif event.type == pygame.MOUSEBUTTONUP:
                with state_lock:
                    control['mouse_pressed'] = False
                    control['last_mouse_x'] = control['mouse_x']
                # on release, trigger release of all voices (或只释放最近一个)
                release_all_voices()
            elif event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                with state_lock:
                    # update positions
                    control['mouse_x'] = x
                    control['mouse_y'] = y
                    dx = x - control['last_mouse_x']
                    control['last_mouse_x'] = x
                    # map vertical to timbre
                    control['timbre'] = np.clip(1.0 - (y / HEIGHT), 0.0, 1.0)
                    # if pressed, do pitch glide / adjust current voice freq
                    if control['mouse_pressed']:
                        # glide: change last voice frequency to new mapped pitch
                        if len(voices) > 0:
                            # slide last voice smoothly toward new freq
                            target_midi = x_to_midi(x)
                            target_freq = midi_to_freq(target_midi)
                            # simple instant change for prototype
                            voices[-1].freq = target_freq
                            # if motion speed large -> treat as "pluck" stronger
                            if hasattr(event, 'rel') and len(event.rel) > 1:
                                speed = np.hypot(dx, event.rel[1])
                            else:
                                speed = abs(dx)
                            # 限制增强幅度的频率，避免过于频繁触发
                            if speed > 8 and (now - last_play_time) > 0.1:
                                voices[-1].amp = min(1.2, voices[-1].amp + 0.6)
                                # re-trigger attack quickly
                                voices[-1].env_state = 'attack'
                                voices[-1].env_time = 0.0
                                last_play_time = now
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    release_all_voices()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    with state_lock:
                        control['pitch_bend'] += 10.0  # cents
                elif event.key == pygame.K_DOWN:
                    with state_lock:
                        control['pitch_bend'] -= 10.0

        draw_ui()
        clock.tick(60)
finally:
    if stream is not None:
        try:
            stream.stop()
            stream.close()
        except Exception as e:
            print(f"关闭音频流时出错: {e}")
    pygame.quit()
