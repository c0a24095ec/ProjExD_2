import time
import os
import random
import sys
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0), 
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]: 
    """
    引数：こうかとんRect or ばくだんRect
    戻り値：判定結果タプル（横方向, 縦方向）
    画面内ならTrue/画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向にはみ出ていたら
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向にはみ出ていたら
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    引数：スクリーンSurface
    戻り値：なし
    Game Over画面を5秒間表示する
    こうかとん画像を左右2つ表示する
    """
    gameover_img = pg.Surface((WIDTH, HEIGHT))
    gameover_img.set_alpha(200)  # 透明度設定
    gameover_img.fill((0, 0, 0))  # 黒で塗りつぶし

    # 白文字でGame Over
    font = pg.font.Font(None, 60)
    text_surf = font.render("Game Over", True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
    gameover_img.blit(text_surf, text_rect)

    # こうかとん画像を左右2つ表示
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rect_left = kk_img.get_rect(center=(WIDTH/2-150, HEIGHT/2))
    kk_rect_right = kk_img.get_rect(center=(WIDTH/2+150, HEIGHT/2))
    gameover_img.blit(kk_img, kk_rect_left)
    gameover_img.blit(kk_img, kk_rect_right)

    # 1のSurfaceをscreenにblit
    screen.blit(gameover_img, (0, 0))
    pg.display.update()
    time.sleep(5)   


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    引数：ばくだんRect
    戻り値：ばくだん画像リスト、加速度リスト
    ばくだんが徐々に大きく、速くなるようにする
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r), pg.SRCALPHA)  # 透過対応Surface
        pg.draw.circle(bb_img, (255, 0, 0, 180), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
        bb_accs.append(r)  # 加速度は1,2,...,10
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    引数：こうかとんRect
    戻り値：こうかとん画像リスト
    押すキーによって効果トンの画像の方向を変える
    """
    kk_dict = {
        (0, 0): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9), True, False),      # キー押下がない場合
        (0, -5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 270, 0.9), True, False),     # 上
        (+5, -5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 315, 0.9), True, False),   # 右上
        (+5, 0): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9), True, False),    # 右
        (+5, +5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 0.9), True, False),  # 右下
        (0, +5): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 0.9), True, False),   # 下
        (-5, +5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 0.9),  # 左下
        (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),   # 左
        (-5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 315, 0.9),  # 左上
    }
    return kk_dict


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 赤い爆弾円
    bb_img.set_colorkey((0, 0, 0))  # 四隅の黒い部分を透過
    bb_rct = bb_img.get_rect()  # 爆弾Rect
    bb_rct.centerx = random.randint(0, WIDTH)  # 爆弾横座標
    bb_rct.centery = random.randint(0, HEIGHT)  # 爆弾縦座標
    vx, vy = +5, +5  # 爆弾の速度
    clock = pg.time.Clock()
    tmr = 0
    bb_imgs, bb_accs = init_bb_imgs()
    kk_imgs = get_kk_imgs()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾の衝突判定
            gameover(screen)
            return  # ゲームオーバー
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] # 横方向の移動量を加算
                sum_mv[1] += mv[1] # 縦方向の移動量を加算
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx, vy)  # 爆弾移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向にはみ出ていたら
            vx *= -1
        if not tate:  # 縦方向にはみ出ていたら
            vy *= -1
        screen.blit(bb_img, bb_rct)  # 爆弾描画
        pg.display.update()
        tmr += 1
        clock.tick(50)
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        acc = bb_accs[idx]
        avx = vx * acc
        avy = vy * acc
        bb_rct.move_ip(avx, avy)
        avx = vx*bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]
        kk_img = kk_imgs[tuple(sum_mv)]


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
