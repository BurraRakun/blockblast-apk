import pygame
import random
import os
import math
import colorsys
import struct
import json

# --- AYARLAR ---
EKRAN_GENISLIK = 500
EKRAN_YUKSEKLIK = 750
IZGARA_BOYUTU = 8
HUCRE_BOYUTU = 50

BASE_IZGARA_OFFSET_X = (EKRAN_GENISLIK - (IZGARA_BOYUTU * HUCRE_BOYUTU)) // 2
BASE_IZGARA_OFFSET_Y = 110 
PARCA_SPAWN_Y = 630
BTN_POWER_Y = 530

DURUM_MENU = 0
DURUM_OYUN = 1
DURUM_PAUSE = 2
DURUM_GAMEOVER = 3
DURUM_MARKET = 4 # Yeni Market Durumu

MOD_KLASIK = 0
MOD_BOMBA = 1
MOD_USTA = 2

BASLANGIC_ALTIN = 20
BEDEL_DONDIR = 10
BEDEL_YENILE = 30
KAZANC_SATIR = 2

RENK_ARKA = (30, 30, 45)
RENK_YAZI = (255, 255, 255)
RENK_SKOR_KUTUSU = (50, 50, 70)
RENK_BTN_NORMAL = (70, 70, 90)
RENK_BTN_HOVER = (100, 100, 130)
RENK_BOMBA_YAZI = (255, 255, 0)
FEVER_PARLAMA = (255, 215, 0) 
RENK_HAYALET = (255, 255, 255, 30)
RENK_ALTIN = (255, 215, 0)
RENK_YESIL = (46, 204, 113)
RENK_KIRMIZI = (231, 76, 60)

# --- TEMA SİSTEMİ ---
TEMALAR = {
    "klasik": {
        "ad": "Klasik",
        "fiyat": 0,
        "renkler": [
            (231, 76, 60), (46, 204, 113), (52, 152, 219), (155, 89, 182),
            (241, 196, 15), (230, 126, 34), (26, 188, 156), (232, 67, 147)
        ]
    },
    "neon": {
        "ad": "Neon Cyber",
        "fiyat": 100,
        "renkler": [
            (255, 0, 128), (0, 255, 255), (128, 255, 0), (255, 255, 0),
            (180, 0, 255), (0, 128, 255), (255, 0, 0), (50, 255, 50)
        ]
    },
    "pastel": {
        "ad": "Yumuşak Pastel",
        "fiyat": 250,
        "renkler": [
            (255, 179, 186), (255, 223, 186), (255, 255, 186), (186, 255, 201),
            (186, 225, 255), (200, 180, 255), (255, 200, 255), (180, 200, 200)
        ]
    },
    "zengin": {
        "ad": "Milyoner (Gold)",
        "fiyat": 1000,
        "renkler": [
            (255, 215, 0), (192, 192, 192), (218, 165, 32), (255, 223, 0),
            (184, 134, 11), (238, 232, 170), (205, 127, 50), (255, 250, 205)
        ]
    }
}

# Varsayılan Global Renk Listesi
AKTIF_RENKLER = TEMALAR["klasik"]["renkler"]

# --- ŞEKİL KÜTÜPHANESİ ---
SEKIL_KUTUPHANESI = {
    "KOLAY": [[(0,0)], [(0,0), (1,0)], [(0,0), (0,1)], [(0,0), (1,1)], [(0,0), (1,0), (0,1)]],
    "ORTA": [[(0,0), (1,0), (2,0)], [(0,0), (0,1), (0,2)], [(0,0), (1,0), (1,1)], [(0,0), (0,1), (1,1)], [(0,0), (0,1), (1,0), (1,1)], [(0,0), (1,0), (2,0), (1,1)]],
    "ZOR": [[(0,0), (1,0), (2,0), (3,0)], [(0,0), (0,1), (0,2), (0,3)], [(0,0), (1,0), (2,0), (3,0), (4,0)], [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2)], [(0,0), (0,1), (0,2), (1,2), (2,2)]]
}

TUM_SEKILLER = []
for k in SEKIL_KUTUPHANESI: TUM_SEKILLER.extend(SEKIL_KUTUPHANESI[k])

# --- KAYIT SİSTEMİ (JSON) ---
DOSYA_ADI = "block_blast_save.json"

def verileri_yukle():
    varsayilan = {
        "high_score": 0,
        "gold": 0,
        "owned_themes": ["klasik"],
        "current_theme": "klasik"
    }
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r") as f:
                data = json.load(f)
                # Eksik anahtar varsa varsayılanla tamamla
                for k, v in varsayilan.items():
                    if k not in data:
                        data[k] = v
                return data
        except:
            return varsayilan
    return varsayilan

def verileri_kaydet(data):
    try:
        with open(DOSYA_ADI, "w") as f:
            json.dump(data, f)
    except:
        pass

# Global Veri Nesnesi
OYUN_VERISI = verileri_yukle()
AKTIF_RENKLER = TEMALAR[OYUN_VERISI["current_theme"]]["renkler"]

# --- YARDIMCI SINIFLAR ---
class UcusanYazi:
    def __init__(self, x, y, metin, renk, boyut=24, omur=60):
        self.x = x
        self.y = y
        self.metin = metin
        self.renk = renk
        self.omur = omur
        self.max_omur = omur
        self.font = pygame.font.SysFont("Verdana", boyut, bold=True)
        self.y_hiz = -1.5 

    def update(self):
        self.y += self.y_hiz
        self.omur -= 1

    def draw(self, screen):
        if self.omur > 0:
            alpha = int((self.omur / self.max_omur) * 255)
            surf = self.font.render(self.metin, True, self.renk)
            surf.set_alpha(alpha)
            shadow = self.font.render(self.metin, True, (0,0,0))
            shadow.set_alpha(alpha)
            screen.blit(shadow, (self.x+2, self.y+2))
            screen.blit(surf, (self.x, self.y))

class SesSentezleyici:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.aktif = True
        except:
            self.aktif = False
            return
        self.sesler = {}
        self.sesleri_olustur()

    def dalga_uret(self, f1, f2, sure, vol=0.1):
        if not self.aktif: return None
        sr = 44100
        ns = int(sr * sure)
        buf = bytearray()
        for i in range(ns):
            t = float(i) / ns
            af = f1 + (f2 - f1) * t
            ph = 2 * math.pi * af * (i / sr)
            val = int(math.sin(ph) * 32767 * vol * (1 - t))
            buf.extend(struct.pack('<h', val) * 2)
        return pygame.mixer.Sound(buffer=buf)

    def sesleri_olustur(self):
        if not self.aktif: return
        self.sesler['secim'] = self.dalga_uret(600, 600, 0.05, 0.05)
        self.sesler['yerles'] = self.dalga_uret(300, 200, 0.1, 0.15)
        self.sesler['patlama'] = self.dalga_uret(400, 800, 0.2, 0.12)
        self.sesler['buton'] = self.dalga_uret(500, 600, 0.1, 0.08)
        self.sesler['rotate'] = self.dalga_uret(800, 1000, 0.1, 0.1) 
        self.sesler['bomba'] = self.dalga_uret(200, 100, 0.3, 0.2) 
        self.sesler['hata'] = self.dalga_uret(150, 100, 0.15, 0.15)
        self.sesler['coin'] = self.dalga_uret(1000, 1500, 0.1, 0.1)
        self.sesler['combo'] = self.dalga_uret(600, 1200, 0.3, 0.15)
        self.sesler['cheat'] = self.dalga_uret(1200, 1200, 0.05, 0.02)
        self.sesler['kaching'] = self.dalga_uret(800, 1200, 0.2, 0.2) # Satın alma sesi

    def cal(self, isim):
        if self.aktif and isim in self.sesler:
            self.sesler[isim].play()

class Buton:
    def __init__(self, x, y, w, h, metin, renk_n=RENK_BTN_NORMAL, renk_h=RENK_BTN_HOVER, t_size=24, sub=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.metin = metin
        self.sub = sub
        self.rn = renk_n
        self.rh = renk_h
        self.hover = False
        self.font = pygame.font.SysFont("Verdana", t_size, bold=True)
        self.sub_font = pygame.font.SysFont("Verdana", 14)
        self.anim = 0

    def guncelle(self, m_pos):
        self.hover = self.rect.collidepoint(m_pos)
        if self.hover: self.anim = min(4, self.anim + 1)
        else: self.anim = max(0, self.anim - 1)

    def tiklandi(self, pos): return self.rect.collidepoint(pos)

    def ciz(self, ekran):
        c = self.rh if self.hover else self.rn
        dy = self.rect.y - self.anim
        pygame.draw.rect(ekran, (20,20,30), (self.rect.x, self.rect.y+4, self.rect.w, self.rect.h), border_radius=12)
        pygame.draw.rect(ekran, c, (self.rect.x, dy, self.rect.w, self.rect.h), border_radius=12)
        txt = self.font.render(self.metin, True, RENK_YAZI)
        ekran.blit(txt, txt.get_rect(center=(self.rect.centerx, self.rect.centery - self.anim - (10 if self.sub else 0))))
        if self.sub:
            stxt = self.sub_font.render(self.sub, True, (200,200,200))
            ekran.blit(stxt, stxt.get_rect(center=(self.rect.centerx, self.rect.centery - self.anim + 15)))

class KucukButon:
    def __init__(self, x, y, txt, c, bedel=0):
        self.rect = pygame.Rect(x, y, 80, 50)
        self.text = txt
        self.c = c
        self.bedel = bedel
        self.hover = False
        self.font = pygame.font.SysFont("Verdana", 18, bold=True)
        self.font_sub = pygame.font.SysFont("Verdana", 12, bold=True)

    def ciz(self, ekran, aktif_mi=True):
        col = (min(255, self.c[0]+30), min(255, self.c[1]+30), min(255, self.c[2]+30)) if self.hover else self.c
        if not aktif_mi: col = (60, 60, 70)
        border = (255,255,255) if aktif_mi else (100,100,100)
        pygame.draw.rect(ekran, col, self.rect, border_radius=8)
        pygame.draw.rect(ekran, border, self.rect, 2, border_radius=8)
        t = self.font.render(self.text, True, (255,255,255) if aktif_mi else (150,150,150))
        ekran.blit(t, t.get_rect(center=(self.rect.centerx, self.rect.centery - 8)))
        if self.bedel > 0:
            tb = self.font_sub.render(f"{self.bedel} Altın", True, RENK_ALTIN if aktif_mi else (150,150,150))
            ekran.blit(tb, tb.get_rect(center=(self.rect.centerx, self.rect.centery + 12)))
    def tiklandi(self, pos): return self.rect.collidepoint(pos)

class DurdurmaButonu:
    def __init__(self):
        self.rect = pygame.Rect(EKRAN_GENISLIK-50, 20, 30, 30)
        self.hover = False
    def ciz(self, ekran):
        c = (200,200,200) if self.hover else (100,100,120)
        pygame.draw.rect(ekran, (50,50,70), self.rect, border_radius=6)
        pygame.draw.rect(ekran, c, (self.rect.x+8, self.rect.y+6, 5, 18), border_radius=2)
        pygame.draw.rect(ekran, c, (self.rect.x+17, self.rect.y+6, 5, 18), border_radius=2)
    def tiklandi(self, pos): return self.rect.collidepoint(pos)

class MarketItem:
    def __init__(self, key, y_pos):
        self.key = key
        self.data = TEMALAR[key]
        self.rect = pygame.Rect(50, y_pos, 400, 80)
        self.btn_rect = pygame.Rect(350, y_pos+20, 90, 40)
        self.font_ad = pygame.font.SysFont("Verdana", 20, bold=True)
        self.font_btn = pygame.font.SysFont("Verdana", 14, bold=True)
        
    def ciz(self, ekran, sahip_mi, secili_mi):
        bg_col = (60, 60, 80) if not secili_mi else (46, 204, 113)
        pygame.draw.rect(ekran, bg_col, self.rect, border_radius=10)
        pygame.draw.rect(ekran, (100,100,120), self.rect, 2, border_radius=10)
        
        # Tema Önizleme (Küçük kutucuklar)
        for i, c in enumerate(self.data["renkler"][:4]):
            pygame.draw.rect(ekran, c, (60 + i*25, self.rect.y+45, 20, 20), border_radius=4)

        isim = self.font_ad.render(self.data["ad"], True, (255,255,255))
        ekran.blit(isim, (60, self.rect.y + 15))

        # Buton Durumu
        btn_renk = (100, 100, 100)
        btn_yazi = ""
        
        if secili_mi:
            btn_renk = (40, 40, 40)
            btn_yazi = "SEÇİLİ"
        elif sahip_mi:
            btn_renk = (52, 152, 219)
            btn_yazi = "SEÇ"
        else:
            can_afford = OYUN_VERISI["gold"] >= self.data["fiyat"]
            btn_renk = RENK_YESIL if can_afford else RENK_KIRMIZI
            btn_yazi = f"{self.data['fiyat']} Altın"

        pygame.draw.rect(ekran, btn_renk, self.btn_rect, border_radius=6)
        t = self.font_btn.render(btn_yazi, True, (255,255,255))
        ekran.blit(t, t.get_rect(center=self.btn_rect.center))

    def tiklandi(self, pos):
        return self.btn_rect.collidepoint(pos)

class Parcacik:
    def __init__(self, x, y, c):
        self.x, self.y, self.c = x, y, c
        self.vx, self.vy = random.uniform(-4,4), random.uniform(-6,-2)
        self.timer, self.size = random.randint(30, 60), random.randint(4,8)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.timer -= 1
        self.size = max(0, self.size-0.1)
    def draw(self, screen, sx, sy):
        if self.size > 0:
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.c, min(255, self.timer*8)), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (self.x+sx, self.y+sy))

class AnimasyonluHucre:
    def __init__(self, gx, gy, c):
        self.gx, self.gy, self.c = gx, gy, c
        self.timer, self.scale, self.finished = 15, 1.0, False
    def update(self):
        self.timer-=1
        self.finished = self.timer<=0
        self.scale = 1.0 + (math.sin(self.timer*0.5)*0.2)
    def draw(self, screen, ox, oy):
        sz = int(HUCRE_BOYUTU*self.scale)
        diff = (sz-HUCRE_BOYUTU)//2
        r = pygame.Rect(ox+self.gx*HUCRE_BOYUTU-diff, oy+self.gy*HUCRE_BOYUTU-diff, sz, sz)
        pygame.draw.rect(screen, (255,255,255), r, border_radius=6)

class Sarsinti:
    def __init__(self):
        self.timer, self.magnitude = 0, 0
    def baslat(self, guc=5, sure=15):
        self.magnitude, self.timer = guc, sure
    def get_offset(self):
        if self.timer > 0:
            self.timer -= 1
            return random.randint(-self.magnitude, self.magnitude), random.randint(-self.magnitude, self.magnitude)
        return 0, 0

class ArkaPlanEfekti:
    def __init__(self):
        self.hue = 0.6
        self.shapes = [{'x':random.randint(0,500), 'y':random.randint(0,750), 'size':random.randint(20,80), 'speed':random.uniform(0.2,1.0), 'alpha':random.randint(10,30)} for _ in range(15)]
        self.panic = 0
    def update(self, fever, doluluk):
        self.hue = (self.hue + (0.02 if fever else 0.0005)) % 1.0
        h = 3 if fever else 1
        for s in self.shapes:
            s['y'] -= s['speed']*h
            if s['y']<-100:
                s['y']=800
                s['x']=random.randint(0,500)
        self.panic = min(100, self.panic+2) if doluluk>0.70 else max(0, self.panic-2)
    def draw(self, screen):
        bg = colorsys.hsv_to_rgb(self.hue, 0.6, 0.2)
        screen.fill((int(bg[0]*255), int(bg[1]*255), int(bg[2]*255)))
        for s in self.shapes:
            surf=pygame.Surface((s['size'],s['size']))
            surf.set_alpha(s['alpha'])
            surf.fill((255,255,255))
            screen.blit(surf, (s['x'],s['y']))
        if self.panic>0:
            s=pygame.Surface((500,750))
            s.fill((255,0,0))
            s.set_alpha(int(self.panic))
            screen.blit(s,(0,0))

class FeverBar:
    def __init__(self):
        self.val, self.max, self.is_fever, self.timer = 0, 100, False, 0
    def add(self, amt):
        if not self.is_fever:
            self.val+=amt
            if self.val>=self.max:
                self.is_fever, self.val, self.timer = True, 100, 600
    def update(self):
        if self.is_fever:
            self.timer-=1
            self.val=(self.timer/600)*100
            self.is_fever=self.timer>0
        elif self.val>0: self.val-=0.2
    def draw(self, screen):
        pygame.draw.rect(screen, (20,20,30), (20,80,460,10), border_radius=5)
        if self.val>0:
            w=(self.val/100)*460
            c=FEVER_PARLAMA if self.is_fever else (52,152,219)
            s=math.sin(pygame.time.get_ticks()*0.1)*2 if self.is_fever else 0
            pygame.draw.rect(screen, c, (20,80+s,w,10), border_radius=5)

class BlokParcasi:
    def __init__(self, x, y, shape, c):
        self.x, self.y, self.ox, self.oy, self.shape, self.c = x, y, x, y, shape, c
        self.drag, self.size = False, 25
        self.update_rects()
    def update_rects(self):
        sz=HUCRE_BOYUTU if self.drag else self.size
        self.rects=[pygame.Rect(self.x+b[0]*sz, self.y+b[1]*sz, sz, sz) for b in self.shape]
    def dondur(self):
        ns=[(-y,x) for x,y in self.shape]
        mx=min(k[0] for k in ns)
        my=min(k[1] for k in ns)
        self.shape=[(k[0]-mx, k[1]-my) for k in ns]
        self.update_rects()
    def w(self): return (max([b[0] for b in self.shape])+1)*self.size
    def ciz(self, screen, sx=0, sy=0):
        ox, oy, sz = (0 if self.drag else sx), (0 if self.drag else sy), (HUCRE_BOYUTU if self.drag else self.size)
        for b in self.shape:
            bx, by = self.x+b[0]*sz+ox, self.y+b[1]*sz+oy
            pygame.draw.rect(screen, self.c, (bx, by, sz, sz), border_radius=8)
            pygame.draw.rect(screen, (0,0,0,30), (bx+2, by+2, sz-4, sz-4), 1, border_radius=6)
            if not self.drag: pygame.draw.rect(screen, (0,0,0,50), (bx, by, sz, sz), 1, border_radius=8)
    def tiklandi(self, pos):
        if not self.rects: return False
        t=self.rects[0].copy()
        for r in self.rects[1:]: t.union_ip(r)
        return t.inflate(40,40).collidepoint(pos)

# --- FONKSİYONLAR ---
def can_place(grid, piece, ix, iy):
    for b in piece.shape:
        hx, hy = ix+b[0], iy+b[1]
        if not (0<=hx<IZGARA_BOYUTU and 0<=hy<IZGARA_BOYUTU) or grid[hy][hx]!=0: return False
    return True

def spawn_pieces():
    ps, pos = [], [70,210,350]
    for i in range(3):
        # AKTIF_RENKLER globalinden renk seç
        renk = random.choice(AKTIF_RENKLER)
        p=BlokParcasi(pos[i],PARCA_SPAWN_Y,random.choice(TUM_SEKILLER), renk)
        p.x, p.ox = pos[i]-p.w()//2, pos[i]-p.w()//2
        p.update_rects()
        ps.append(p)
    return ps

def tahmin_ve_hayalet_ciz(screen, parca, grid, ox, oy):
    gx = int((parca.x - ox + HUCRE_BOYUTU/2) // HUCRE_BOYUTU)
    gy = int((parca.y - oy + HUCRE_BOYUTU/2) // HUCRE_BOYUTU)
    if can_place(grid, parca, gx, gy):
        piece_cells = [(gy+b[1], gx+b[0]) for b in parca.shape]
        
        temp_grid = [row[:] for row in grid]
        for b in parca.shape: temp_grid[gy+b[1]][gx+b[0]] = 1
        full_rows = [r for r in range(IZGARA_BOYUTU) if all(temp_grid[r])]
        full_cols = [c for c in range(IZGARA_BOYUTU) if all(temp_grid[r][c] for r in range(IZGARA_BOYUTU))]

        flash_alpha = int(100 + math.sin(pygame.time.get_ticks()*0.01)*50)
        flash_surf_h = pygame.Surface((IZGARA_BOYUTU*HUCRE_BOYUTU, HUCRE_BOYUTU), pygame.SRCALPHA)
        flash_surf_h.fill((255,255,255,flash_alpha))
        flash_surf_v = pygame.Surface((HUCRE_BOYUTU, IZGARA_BOYUTU*HUCRE_BOYUTU), pygame.SRCALPHA)
        flash_surf_v.fill((255,255,255,flash_alpha))

        for r in full_rows: screen.blit(flash_surf_h, (ox, oy + r*HUCRE_BOYUTU))
        for c in full_cols: screen.blit(flash_surf_v, (ox + c*HUCRE_BOYUTU, oy))

        s = pygame.Surface((HUCRE_BOYUTU, HUCRE_BOYUTU), pygame.SRCALPHA)
        s.fill(RENK_HAYALET)
        for b in parca.shape:
            bx, by = ox+(gx+b[0])*HUCRE_BOYUTU, oy+(gy+b[1])*HUCRE_BOYUTU
            screen.blit(s, (bx, by))
            pygame.draw.rect(screen, (255,255,255,80), (bx,by,HUCRE_BOYUTU,HUCRE_BOYUTU), 2, border_radius=4)

# --- MAIN LOOP ---
def main():
    global AKTIF_RENKLER, OYUN_VERISI # Global değişkenleri kullan
    
    pygame.init()
    screen = pygame.display.set_mode((EKRAN_GENISLIK, EKRAN_YUKSEKLIK))
    pygame.display.set_caption("Block Blast V29 - Market System")
    clock = pygame.time.Clock()
    
    font_logo=pygame.font.SysFont("Verdana", 45, bold=True)
    font_skor=pygame.font.SysFont("Verdana", 24, bold=True)
    font_high=pygame.font.SysFont("Verdana", 14, bold=True)
    font_bomba=pygame.font.SysFont("Verdana", 24, bold=True)
    font_coin=pygame.font.SysFont("Verdana", 20, bold=True)
    font_combo=pygame.font.SysFont("Verdana", 40, bold=True)
    
    izgara = [[0]*IZGARA_BOYUTU for _ in range(IZGARA_BOYUTU)]
    bombalar = {}
    parcalar = []
    parcaciklar = []
    animlar = []
    ucusan_yazilar = []
    bg = ArkaPlanEfekti()
    fever = FeverBar()
    ses = SesSentezleyici()
    sarsinti = Sarsinti()
    
    mode = MOD_KLASIK
    skor = 0
    # Altın OYUN_VERISI'nden okunacak
    state = DURUM_MENU
    
    combo_sayaci = 0 
    hile_aktif = False 
    
    btn_k = Buton(150, 300, 200, 70, "KLASİK", sub="Sınırsız")
    btn_b = Buton(150, 390, 200, 70, "BOMBA", (90,40,40),(120,60,60), sub="Zamana Karşı")
    btn_u = Buton(150, 480, 200, 70, "USTA", (40,60,90),(60,80,120), sub="Ekonomili")
    btn_shop = Buton(150, 580, 200, 50, "MARKET", (150, 100, 0), (200, 150, 0)) # Yeni Market Butonu

    btn_t = Buton(150, 450, 200, 50, "TEKRAR")
    btn_m = Buton(150, 520, 200, 50, "MENÜ")
    btn_market_geri = Buton(380, 680, 100, 40, "GERİ", t_size=16)

    pause_icon = DurdurmaButonu()
    
    btn_rot = KucukButon(160, BTN_POWER_Y, "Döndür", (46,204,113), BEDEL_DONDIR)
    btn_ref = KucukButon(260, BTN_POWER_Y, "Yenile", (52,152,219), BEDEL_YENILE)
    
    market_items = []
    y_off = 100
    for k in TEMALAR:
        market_items.append(MarketItem(k, y_off))
        y_off += 90

    held = None
    dx=0
    dy=0
    bomb_counter=0

    running = True
    while running:
        m_pos = pygame.mouse.get_pos()
        fill_rate = sum(1 for r in izgara for c in r if c!=0)/64
        bg.update(fever.is_fever, fill_rate if state==DURUM_OYUN else 0)
        shake_x, shake_y = sarsinti.get_offset()

        if state == DURUM_MENU:
            bg.draw(screen)
            l=font_logo.render("BLOCK BLAST",True,FEVER_PARLAMA)
            screen.blit(l,(250-l.get_width()//2,100))
            
            # Altın Göstergesi
            pygame.draw.rect(screen, (60, 50, 20), (350, 20, 130, 40), border_radius=10)
            pygame.draw.circle(screen, RENK_ALTIN, (370, 40), 10)
            c_txt = font_coin.render(str(OYUN_VERISI["gold"]), True, RENK_ALTIN)
            screen.blit(c_txt, (390, 28))

            btn_k.ciz(screen); btn_b.ciz(screen); btn_u.ciz(screen); btn_shop.ciz(screen)
            btn_k.guncelle(m_pos); btn_b.guncelle(m_pos); btn_u.guncelle(m_pos); btn_shop.guncelle(m_pos)
            
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                if e.type==pygame.MOUSEBUTTONDOWN:
                    s=-1
                    if btn_k.tiklandi(m_pos): s=MOD_KLASIK
                    elif btn_b.tiklandi(m_pos): s=MOD_BOMBA
                    elif btn_u.tiklandi(m_pos): s=MOD_USTA
                    elif btn_shop.tiklandi(m_pos): 
                        ses.cal('buton')
                        state = DURUM_MARKET
                    
                    if s!=-1:
                        ses.cal('buton')
                        mode=s
                        izgara=[[0]*8 for _ in range(8)]
                        bombalar={}
                        hile_aktif = False 
                        parcalar=spawn_pieces()
                        skor=0
                        # Altını resetlemiyoruz, birikiyor
                        bomb_counter=0
                        fever=FeverBar()
                        parcaciklar=[]
                        animlar=[]
                        ucusan_yazilar=[]
                        combo_sayaci = 0
                        state=DURUM_OYUN
        
        elif state == DURUM_MARKET:
            bg.draw(screen)
            # Başlık
            t = font_logo.render("MARKET", True, RENK_ALTIN)
            screen.blit(t, (250-t.get_width()//2, 30))
            
            # Altın Göstergesi
            pygame.draw.rect(screen, (60, 50, 20), (350, 20, 130, 40), border_radius=10)
            pygame.draw.circle(screen, RENK_ALTIN, (370, 40), 10)
            c_txt = font_coin.render(str(OYUN_VERISI["gold"]), True, RENK_ALTIN)
            screen.blit(c_txt, (390, 28))

            btn_market_geri.guncelle(m_pos)
            btn_market_geri.ciz(screen)

            for item in market_items:
                sahip = item.key in OYUN_VERISI["owned_themes"]
                secili = item.key == OYUN_VERISI["current_theme"]
                item.ciz(screen, sahip, secili)

            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                if e.type==pygame.MOUSEBUTTONDOWN:
                    if btn_market_geri.tiklandi(m_pos):
                        ses.cal('buton')
                        state = DURUM_MENU
                    
                    for item in market_items:
                        if item.tiklandi(m_pos):
                            if item.key in OYUN_VERISI["owned_themes"]:
                                # Zaten sahip, seç
                                OYUN_VERISI["current_theme"] = item.key
                                AKTIF_RENKLER = TEMALAR[item.key]["renkler"]
                                ses.cal('secim')
                                verileri_kaydet(OYUN_VERISI)
                            elif OYUN_VERISI["gold"] >= item.data["fiyat"]:
                                # Satın al
                                OYUN_VERISI["gold"] -= item.data["fiyat"]
                                OYUN_VERISI["owned_themes"].append(item.key)
                                ses.cal('kaching') # Para sesi
                                verileri_kaydet(OYUN_VERISI)
                            else:
                                ses.cal('hata')

        elif state == DURUM_OYUN:
            bg.draw(screen)
            pause_icon.hover=pause_icon.rect.collidepoint(m_pos)
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                
                # --- HİLE KODU (H TUŞU) ---
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_h:
                        hile_aktif = not hile_aktif
                        ses.cal('cheat')
                # --------------------------------

                if e.type==pygame.MOUSEBUTTONDOWN:
                    if pause_icon.tiklandi(e.pos):
                        state=DURUM_PAUSE
                    elif mode==MOD_USTA and not held:
                        if btn_rot.tiklandi(e.pos): 
                            if OYUN_VERISI["gold"] >= BEDEL_DONDIR:
                                OYUN_VERISI["gold"] -= BEDEL_DONDIR
                                verileri_kaydet(OYUN_VERISI)
                                ses.cal('rotate')
                                [p.dondur() for p in parcalar]
                            else: ses.cal('hata')
                        elif btn_ref.tiklandi(e.pos): 
                            if OYUN_VERISI["gold"] >= BEDEL_YENILE:
                                OYUN_VERISI["gold"] -= BEDEL_YENILE
                                verileri_kaydet(OYUN_VERISI)
                                ses.cal('secim')
                                parcalar=spawn_pieces()
                            else: ses.cal('hata')
                                
                    if not held:
                        for p in reversed(parcalar):
                            if p.tiklandi(e.pos):
                                held=p; held.drag=True
                                dx, dy = e.pos[0]-p.x, e.pos[1]-p.y
                                parcalar.remove(p); parcalar.append(p)
                                ses.cal('secim')
                                break
                if e.type==pygame.MOUSEBUTTONUP and held:
                    gx=int((held.x-BASE_IZGARA_OFFSET_X+25)//50)
                    gy=int((held.y-BASE_IZGARA_OFFSET_Y+25)//50)
                    if can_place(izgara, held, gx, gy):
                        ses.cal('yerles')
                        
                        temel_puan = len(held.shape)*5
                        if hile_aktif: temel_puan *= 2 
                        
                        ucusan_yazilar.append(UcusanYazi(held.x, held.y, f"+{temel_puan}", (200,200,200), 20))
                        
                        skor+=temel_puan
                        for b in held.shape:
                            izgara[gy+b[1]][gx+b[0]]=held.c
                            animlar.append(AnimasyonluHucre(gx+b[0], gy+b[1], held.c))
                        
                        rows=[y for y in range(8) if all(izgara[y])]
                        cols=[x for x in range(8) if all(izgara[y][x] for y in range(8))]
                        
                        if rows or cols:
                            combo_sayaci += 1
                            ses.cal('patlama')
                            temizlenen_sayisi = len(rows) + len(cols)
                            fever.add(20+temizlenen_sayisi*10)
                            sarsinti.baslat(guc=5 + temizlenen_sayisi + combo_sayaci, sure=15)
                            
                            kazanc = temizlenen_sayisi * 100 * combo_sayaci
                            if hile_aktif: kazanc *= 2
                            
                            skor += kazanc
                            
                            text_pos_x = BASE_IZGARA_OFFSET_X + 200
                            text_pos_y = BASE_IZGARA_OFFSET_Y + 200
                            ucusan_yazilar.append(UcusanYazi(text_pos_x-40, text_pos_y-50, f"+{kazanc}", FEVER_PARLAMA, 36))
                            
                            if combo_sayaci > 1:
                                ses.cal('combo')
                                ucusan_yazilar.append(UcusanYazi(text_pos_x-60, text_pos_y, f"COMBO x{combo_sayaci}!", (255, 100, 100), 40))
                            
                            if temizlenen_sayisi >= 3:
                                ucusan_yazilar.append(UcusanYazi(text_pos_x-50, text_pos_y+40, "EFSANE!", (100, 255, 255), 30))
                            elif temizlenen_sayisi >= 2:
                                ucusan_yazilar.append(UcusanYazi(text_pos_x-50, text_pos_y+40, "HARİKA!", (100, 255, 100), 30))

                            # Usta modunda altın kazan, HER MODDA KAYDET
                            if mode == MOD_USTA:
                                altin_kazanc = temizlenen_sayisi * KAZANC_SATIR
                                if hile_aktif: altin_kazanc *= 2 
                                OYUN_VERISI["gold"] += altin_kazanc
                                verileri_kaydet(OYUN_VERISI)
                                ses.cal('coin')
                                ucusan_yazilar.append(UcusanYazi(400, 60, f"+{altin_kazanc} Gold", RENK_ALTIN, 20))

                            for y in rows:
                                for x in range(8):
                                    if (y,x) in bombalar: del bombalar[(y,x)]
                                    for _ in range(5): parcaciklar.append(Parcacik(BASE_IZGARA_OFFSET_X+x*50+25, BASE_IZGARA_OFFSET_Y+y*50+25, izgara[y][x]))
                                    izgara[y][x]=0
                            for x in cols:
                                for y in range(8):
                                    if (y,x) in bombalar: del bombalar[(y,x)]
                                    if izgara[y][x]!=0:
                                        for _ in range(5): parcaciklar.append(Parcacik(BASE_IZGARA_OFFSET_X+x*50+25, BASE_IZGARA_OFFSET_Y+y*50+25, izgara[y][x]))
                                        izgara[y][x]=0
                        else:
                            combo_sayaci = 0
                        
                        if mode==MOD_BOMBA:
                            for k in list(bombalar.keys()):
                                bombalar[k]-=1
                                if bombalar[k]<=0: state=DURUM_GAMEOVER
                            bomb_counter+=1
                            if bomb_counter>=3 and state!=DURUM_GAMEOVER:
                                empty=[(y,x) for y in range(8) for x in range(8) if izgara[y][x]!=0 and (y,x) not in bombalar]
                                if empty:
                                    pos=random.choice(empty)
                                    bombalar[pos]=9
                                    ses.cal('bomba')
                                    bomb_counter=0

                        parcalar.remove(held)
                        if not parcalar: parcalar=spawn_pieces()
                        
                        dead=True
                        for p in parcalar:
                            tp=BlokParcasi(0,0,p.shape,p.c)
                            rotations = 4 if mode==MOD_USTA else 1
                            for _ in range(rotations):
                                if any(can_place(izgara, tp, x, y) for y in range(8) for x in range(8)):
                                    dead=False
                                    break
                                tp.dondur()
                            if not dead: break
                        if dead: state=DURUM_GAMEOVER
                        if skor>OYUN_VERISI["high_score"]:
                            OYUN_VERISI["high_score"]=skor
                            verileri_kaydet(OYUN_VERISI)
                    else:
                        ses.cal('hata')
                        held.x, held.y, held.drag = held.ox, held.oy, False
                        held.update_rects()
                    held=None
                if e.type==pygame.MOUSEMOTION and held:
                    held.x, held.y = e.pos[0]-dx, e.pos[1]-dy
                    held.update_rects()

            fever.update()
            fever.draw(screen)
            
            # --- SKOR PANELİ ---
            pygame.draw.rect(screen, RENK_SKOR_KUTUSU, (20,20,140,75), border_radius=10)
            screen.blit(font_skor.render(f"{skor}",True,RENK_YAZI),(30,25))
            screen.blit(font_high.render(f"En İyi: {OYUN_VERISI['high_score']}",True,(180,180,200)),(30,60))
            
            if combo_sayaci > 1:
                combo_text = font_coin.render(f"Combo: x{combo_sayaci}", True, (255, 100, 100))
                screen.blit(combo_text, (30, 100))

            if mode == MOD_USTA:
                coin_rect = pygame.Rect(170, 20, 100, 60)
                pygame.draw.rect(screen, (60, 50, 20), coin_rect, border_radius=10)
                pygame.draw.circle(screen, RENK_ALTIN, (190, 50), 10)
                coin_txt = font_coin.render(str(OYUN_VERISI["gold"]), True, RENK_ALTIN)
                screen.blit(coin_txt, (210, 38))

            pause_icon.ciz(screen)

            ox, oy = BASE_IZGARA_OFFSET_X+shake_x, BASE_IZGARA_OFFSET_Y+shake_y
            pygame.draw.rect(screen, (60,40,50) if fever.is_fever else (35,35,50), (ox-5, oy-5, 410, 410), border_radius=12)
            for y in range(8):
                for x in range(8):
                    r=pygame.Rect(ox+x*50, oy+y*50, 50, 50)
                    pygame.draw.rect(screen, (45,45,60), r.inflate(-2,-2), border_radius=4)
                    if izgara[y][x]!=0:
                        c=izgara[y][x] if not fever.is_fever else FEVER_PARLAMA
                        if (y,x) in bombalar:
                            c=(255, 50+int(200*abs(math.sin(pygame.time.get_ticks()*0.01))), 50)
                        pygame.draw.rect(screen, c, r.inflate(-2,-2), border_radius=8)
                        pygame.draw.rect(screen, (0,0,0,30), r.inflate(-6,-6), 1, border_radius=6)
                        if (y,x) in bombalar:
                            t=font_bomba.render(str(bombalar[(y,x)]),True,(255,255,255))
                            screen.blit(t,t.get_rect(center=r.center))

            if held and held.drag: tahmin_ve_hayalet_ciz(screen, held, izgara, ox, oy)
            for a in animlar[:]:
                a.update(); a.draw(screen, ox, oy)
                if a.finished: animlar.remove(a)
            
            for u in ucusan_yazilar[:]:
                u.update(); u.draw(screen)
                if u.omur <= 0: ucusan_yazilar.remove(u)

            pygame.draw.line(screen, (60,60,80), (0,560), (500,560), 3)
            
            if mode==MOD_USTA:
                btn_rot.hover=btn_rot.rect.collidepoint(m_pos)
                btn_ref.hover=btn_ref.rect.collidepoint(m_pos)
                btn_rot.ciz(screen, aktif_mi=(OYUN_VERISI["gold"] >= BEDEL_DONDIR))
                btn_ref.ciz(screen, aktif_mi=(OYUN_VERISI["gold"] >= BEDEL_YENILE))

            for p in parcalar: p.ciz(screen, shake_x, shake_y)
            for p in parcaciklar[:]:
                p.update(); p.draw(screen, shake_x, shake_y)
                if p.timer<=0: parcaciklar.remove(p)

        elif state == DURUM_PAUSE:
            btn_d=Buton(150,320,200,50,"DEVAM"); btn_a=Buton(150,390,200,50,"MENÜ")
            s=pygame.Surface((500,750)); s.set_alpha(150); s.fill((0,0,0)); screen.blit(s,(0,0))
            btn_d.guncelle(m_pos); btn_a.guncelle(m_pos)
            btn_d.ciz(screen); btn_a.ciz(screen)
            for e in pygame.event.get():
                if e.type==pygame.MOUSEBUTTONDOWN:
                    if btn_d.tiklandi(m_pos): state=DURUM_OYUN
                    elif btn_a.tiklandi(m_pos): state=DURUM_MENU

        elif state == DURUM_GAMEOVER:
            s=pygame.Surface((500,750)); s.set_alpha(200); s.fill((10,10,20)); screen.blit(s,(0,0))
            t1=font_logo.render("OYUN BİTTİ",True,(255,80,80))
            screen.blit(t1,(250-t1.get_width()//2,150))
            t2=font_skor.render(f"SKOR: {skor}",True,(255,255,255))
            screen.blit(t2,(250-t2.get_width()//2,220))
            btn_t.guncelle(m_pos); btn_m.guncelle(m_pos)
            btn_t.ciz(screen); btn_m.ciz(screen)
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                if e.type==pygame.MOUSEBUTTONDOWN:
                    if btn_t.tiklandi(m_pos):
                         ses.cal('buton')
                         izgara=[[0]*8 for _ in range(8)]
                         bombalar={}
                         hile_aktif = False
                         parcalar=spawn_pieces()
                         skor, bomb_counter, combo_sayaci = 0, 0, 0
                         # Altın sıfırlanmaz
                         parcaciklar, animlar, ucusan_yazilar = [], [], []
                         state=DURUM_OYUN
                    elif btn_m.tiklandi(m_pos):
                         ses.cal('buton'); state=DURUM_MENU

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()