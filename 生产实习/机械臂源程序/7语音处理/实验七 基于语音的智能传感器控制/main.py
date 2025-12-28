import audio
import time

from Maix import GPIO, I2S
from fpioa_manager import fm

from machine import SPI

spi = SPI(SPI.SPI0, mode=SPI.MODE_MASTER, baudrate=10000000, polarity=0, phase=0, bits=8, firstbit=SPI.MSB, sck=25,
          mosi=24)  # 定义彩色灯环引脚

# user setting
sample_rate = 16000
record_time = 4  # s


###############################################################
# LED灯环驱动
def on_led(lun, data):  # 彩色灯环控制(亮度，颜色)
    spi.write(0x00)
    spi.write(0x00)
    spi.write(0x00)
    spi.write(0x00)
    for i in range(12):
        spi.write(0xe0 + lun[i])
        spi.write(data[0])
        spi.write(data[1])
        spi.write(data[2])
    spi.write(0xff)
    spi.write(0xff)
    spi.write(0xff)
    spi.write(0xff)


###############################################################

###############################################################
# LED灯环控制
c = [0, 45, 200]
js = 0


def LED_():
    for q in range(12):
        a = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]  # 让12个灯亮度为2
        a[q] = 20  # 让要突出亮的灯亮度为20
        on_led(a, c)  # 彩色灯环控制(亮度，颜色)
        # print(a)
        time.sleep(0.02)  # 休眠0.02秒
    a = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]  # 让12个灯亮度为2
    on_led(a, c)


###############################################################

###############################################################
# 声音播放控制
def PLAY_(wav):
    wav_dev = I2S(I2S.DEVICE_1)
    player = audio.Audio(path=wav)  # path="/flash/yikaiqi.wav"# 引用播放文件
    player.volume(50)  # 音量
    # read audio info
    wav_info = player.play_process(wav_dev)  # 读取文件
    # print("wav file head information: ", wav_info)
    # config i2s according to audio info
    wav_dev.channel_config(wav_dev.CHANNEL_1, wav_dev.TRANSMITTER, align_mode=I2S.RIGHT_JUSTIFYING_MODE)  # 使用该设备播放
    wav_dev.set_sample_rate(wav_info[1])

    audio_en.value(1)  # 使能功放
    while True:
        ret1 = player.play()  # 播放
        if ret1 == 0:
            # print("end")
            break
    player.finish()  # 结束播放
    audio_en.value(0)  # 关闭功放


###############################################################


###############################################################
# 麦克风 扬声器 定义 初始化
AUDIO_PA_EN_PIN = 32  # Maix Go(version 2.20)功放使能引脚

# open audio PA
if AUDIO_PA_EN_PIN:
    fm.register(AUDIO_PA_EN_PIN, fm.fpioa.GPIO1, force=True)
    audio_en = GPIO(GPIO.GPIO1, GPIO.OUT)
    audio_en.value(0)

# 麦克风
# 引脚，左右，标号
# 20  1  6
# 21  0  4
# 21  1  5
# 22  0  2
# 22  1  3
# 23  0  0
# 23  1  1

# bit & duino定义麦克风
fm.register(20, fm.fpioa.I2S0_IN_D0, force=True)
fm.register(18, fm.fpioa.I2S0_SCLK, force=True)
fm.register(19, fm.fpioa.I2S0_WS, force=True)
# register i2s(i2s0) pin数字扬声器引脚
fm.register(34, fm.fpioa.I2S1_OUT_D1, force=True)
fm.register(35, fm.fpioa.I2S1_SCLK, force=True)
fm.register(33, fm.fpioa.I2S1_WS, force=True)

# init i2s(i2s0)扬声器初始化
wav_dev = I2S(I2S.DEVICE_1)
wav_dev.channel_config(wav_dev.CHANNEL_1, wav_dev.TRANSMITTER, align_mode=I2S.RIGHT_JUSTIFYING_MODE)

rx = I2S(I2S.DEVICE_0)  # 麦克风初始化
rx.channel_config(rx.CHANNEL_0, rx.RECEIVER, align_mode=I2S.STANDARD_MODE)
rx.set_sample_rate(sample_rate)
# print(rx)
###############################################################
LED_()  # LED灯环控制
###############################################################
from speech_recognizer import asr


# 定义声学模型词，与模型对应
class maix_asr(asr):
    asr_vocab = ["lv", "shi", "yang", "chun", "yan", "jing", "da", "kuai", "wen", "zhang", "de", "di", "se", "si",
                 "yue", "lin", "luan", "geng", "xian", "huo", "xiu", "mei", "yi", "ang", "ran", "ta", "jin", "ping",
                 "yao", "bu", "li", "liang", "zai", "yong", "dao", "shang", "xia", "fan", "teng", "dong", "she", "xing",
                 "zhuang", "ru", "hai", "tun", "zhi", "tou", "you", "ling", "pao", "hao", "le", "zha", "zen", "me",
                 "zheng", "cai", "ya", "shu", "tuo", "qu", "fu", "guang", "bang", "zi", "chong", "shui", "cuan", "ke",
                 "shei", "wan", "hou", "zhao", "jian", "zuo", "cu", "hei", "yu", "ce", "ming", "dui", "cheng", "men",
                 "wo", "bei", "dai", "zhe", "hu", "jiao", "pang", "ji", "lao", "nong", "kang", "yuan", "chao", "hui",
                 "xiang", "bing", "qi", "chang", "nian", "jia", "tu", "bi", "pin", "xi", "zou", "chu", "cun", "wang",
                 "na", "ge", "an", "ning", "tian", "xiao", "zhong", "shen", "nan", "er", "ri", "zhu", "xin", "wai",
                 "luo", "gang", "qing", "xun", "te", "cong", "gan", "lai", "he", "dan", "wei", "die", "kai", "ci", "gu",
                 "neng", "ba", "bao", "xue", "shuai", "dou", "cao", "mao", "bo", "zhou", "lie", "qie", "ju", "chuan",
                 "guo", "lan", "ni", "tang", "ban", "su", "quan", "huan", "ying", "a", "min", "meng", "wu", "tai",
                 "hua", "xie", "pai", "huang", "gua", "jiang", "pian", "ma", "jie", "wa", "san", "ka", "zong", "nv",
                 "gao", "ye", "biao", "bie", "zui", "ren", "jun", "duo", "ze", "tan", "mu", "gui", "qiu", "bai", "sang",
                 "jiu", "yin", "huai", "rang", "zan", "shuo", "sha", "ben", "yun", "la", "cuo", "hang", "ha", "tuan",
                 "gong", "shan", "ai", "kou", "zhen", "qiong", "ding", "dang", "que", "weng", "qian", "feng", "jue",
                 "zhuan", "ceng", "zu", "bian", "nei", "sheng", "chan", "zao", "fang", "qin", "e", "lian", "fa", "lu",
                 "sun", "xu", "deng", "guan", "shou", "mo", "zhan", "po", "pi", "gun", "shuang", "qiang", "kao", "hong",
                 "kan", "dian", "kong", "pei", "tong", "ting", "zang", "kuang", "reng", "ti", "pan", "heng", "chi",
                 "lun", "kun", "han", "lei", "zuan", "man", "sen", "duan", "leng", "sui", "gai", "ga", "fou", "kuo",
                 "ou", "suo", "sou", "nu", "du", "mian", "chou", "hen", "kua", "shao", "rou", "xuan", "can", "sai",
                 "dun", "niao", "chui", "chen", "hun", "peng", "fen", "cang", "gen", "shua", "chuo", "shun", "cha",
                 "gou", "mai", "liu", "diao", "tao", "niu", "mi", "chai", "long", "guai", "xiong", "mou", "rong", "ku",
                 "song", "che", "sao", "piao", "pu", "tui", "lang", "chuang", "keng", "liao", "miao", "zhui", "nai",
                 "lou", "bin", "juan", "zhua", "run", "zeng", "ao", "re", "pa", "qun", "lia", "cou", "tie", "zhai",
                 "kuan", "kui", "cui", "mie", "fei", "tiao", "nuo", "gei", "ca", "zhun", "nie", "mang", "zhuo", "pen",
                 "zun", "niang", "suan", "nao", "ruan", "qiao", "fo", "rui", "rao", "ruo", "zei", "en", "za", "diu",
                 "nve", "sa", "nin", "shai", "nen", "ken", "chuai", "shuan", "beng", "ne", "lve", "qia", "jiong", "pie",
                 "seng", "nuan", "nang", "miu", "pou", "cen", "dia", "o", "zhuai", "yo", "dei", "n", "ei", "nou", "bia",
                 "eng", "den", "_"]

    def get_asr_list(string='xiao-ai-fas-tong-xue'):
        return [__class__.asr_vocab.index(t) for t in string.split('-') if t in __class__.asr_vocab]

    def get_asr_string(listobj=[117, 214, 257, 144]):
        return '-'.join([__class__.asr_vocab[t] for t in listobj if t < len(__class__.asr_vocab)])

    def unit_test():
        print(__class__.get_asr_list('xiao-ai'))
        print(__class__.get_asr_string(__class__.get_asr_list('xiao-ai-fas-tong-xue')))

    def config(self, sets):
        self.set([(sets[key], __class__.get_asr_list(key)) for key in sets])

    def recognize(self):
        res = self.result()
        # print(tmp)
        if res != None:
            sets = {}
            for tmp in res:
                sets[__class__.get_asr_string(tmp[1])] = tmp[0]
                # print(tmp[0], get_asr_string(tmp[1]))
            return sets
        return None


from machine import Timer


def on_timer(timer):
    # print("time up:",timer)
    # print("param:",timer.callback_arg())
    timer.callback_arg().state()


try:
    # default: maix dock / maix duino set shift=0
    t = maix_asr(0x500000, I2S.DEVICE_0, 3, shift=1)  # maix bit set shift=1使能麦克风
    tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PERIODIC, period=64, callback=on_timer, arg=t)
    tim.start()

    # for i in range(50):
    # time.sleep_ms(100)
    # t.stop()
    # for i in range(50):
    # time.sleep_ms(100)
    # t.run()

    t.config({  # 定义识别词条(关键字，匹配阈值)
        'ni-hao': 0.3,
        'kai-deng': 0.2,
        'kai-feng-san': 0.2,
        'guan-deng': 0.2,
        'guan-feng-san': 0.2,
        'xian-shi-wen-du': 0.2,
    })
    print("OK")
    while True:
        tmp = t.recognize()
        if tmp != None:

            if "kai-deng" in tmp:
                print("AA_kai-deng_BB")
                LED_()  # LED灯环控制
                PLAY_("/flash/yikaiqi.wav")  # 声音播放控制

            elif "guan-deng" in tmp:
                print("AA_guan-deng_BB")
                LED_()  # LED灯环控制
                PLAY_("/flash/yiguanbi.wav")  # 声音播放控制

            elif "kai-feng-san" in tmp:
                print("AA_kai-feng-san_BB")
                LED_()  # LED灯环控制
                PLAY_("/flash/yikaiqi.wav")  # 声音播放控制

            elif "guan-feng-san" in tmp:
                print("AA_guan-feng-san_BB")
                LED_()  # LED灯环控制
                PLAY_("/flash/yiguanbi.wav")  # 声音播放控制

            elif "ni-hao" in tmp:
                # print("AA_ni-hao_BB")
                LED_()  # LED灯环控制
                PLAY_("/flash/wozai.wav")  # 声音播放控制

            elif "xian-shi-wen-du" in tmp:
                print("AA_xian-shi-wen-du_BB")
                LED_()  # LED灯环控制
                PLAY_("/flash/haode.wav")  # 声音播放控制



except Exception as e:
    print(e)
finally:
    tim.stop()
    t.__del__()
    del t
