import json, time, os
from os import makedirs
from os.path import exists
import logging, asyncio
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
from multiprocessing.dummy import Pool

"""
要完成的目标：
    1.获取某目录下的所有文件名 √
    2.筛选文件后缀为.html的文件，保存并构建一系列url供爬取 √
    3.爬取每个日志的队友id，职业，自己的单体，总体 √ 
    4.根据boss分类（因为是根据boss的日志爬的），再根据录制者挑某一天的所有日志 √
    5.排除dps垫底的和倒数第二的人（奶燃、敏捷位）
    6.保存为JSON文件
    7.读取JSON文件进行绘图，需要自己某职业的dps演变曲线，最大值，最小值，中位数，
用到的技术：
    1.pyppeteer爬虫
    2.多线程爬虫（没解决）
    3.文件目录获取，JSON文件保存
    4.中等样本量的列表套字典处理
    5.函数式编程
    6.绘图（未完成）
"""
LIST_OF_LOG_DIR = []
DAMAGE = []
RESULT_ALL = []
pass_line = [
    ["多形态机动火炮", "噩梦神谕司", "无尽折磨者恩索利斯", "Skorvald CM", "阿克"],
    [18000, 22000, 20000, 10000, 20000]
]
Failure_List = []
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')
TIMEOUT = 5
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
RESULTS_DIR = 'results_guild_war'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)
HEADLESS = True
browser, tab = None, None
# 文件路径注意转义字符，在路径字符串前面加r，即保持字符原始值的意思
# path = r'C:\Users\Lenovo\Documents\Guild Wars 2\addons\arcdps\arcdps.cbtlogs\多形态机动火炮\路荆\可燃乌龙猹'
path = r'E:\日志分析测试\html'


def filter_html(filename):
    # 该函数用于筛选目标目录中的HTML文件，是的话返回文件名，不是的话返回FALSE
    return '.html' in filename and os.path.splitext(filename)[1] == '.html' or False


# use the above function to filter the files in the current directory
def init_file():
    for file_name in os.listdir(path):
        """
            把html文件加入列表
        """
        if filter_html(file_name):
            LIST_OF_LOG_DIR.append(os.path.join(path, file_name))  # add the path to the log dir


# 文件绝对路径列表没有问题

async def init():
    """
    初始化pyppeteer
    去掉提示框，设置长宽，取消提示框
    """
    global browser, tab
    browser = await launch(headless=HEADLESS,
                           handleSIGINT=True,
                           args=['--disable-infobars',
                                 f'--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}'],
                           )
    tab = await browser.newPage()
    await tab.setViewport({'width': WINDOW_WIDTH, 'height': WINDOW_HEIGHT})


async def scrape_page(url, selector):
    """
    通用的爬取方法
    :param url:爬取的url
    :param selector:CSS选择器
    """
    logging.info('scraping %s', url)
    try:
        await tab.goto(url)
        await tab.waitForSelector(selector, options={
            'timeout': TIMEOUT * 1000  # 等待5秒，因为单位是毫秒所以*1000
        })
    except TimeoutError:
        logging.error('error occurred while scraping %s', url)


def Replace_Mistlock_Instability(str):
    """
      替换雾锁异变
    """
    if "Adrenaline Rush" in str:
        return "怒气迸发"
    elif "Afflicted" in str:
        return "恶疾缠身"
    elif "Boon Overload" in str:
        return "增益过载"
    elif "Flux Bomb" in str:
        return "流体炸弹"
    elif "Fractal Vindicator" in str:
        return "碎层捍卫者"
    elif "Frailty" in str:
        return "脆弱"
    elif "Hamstrung" in str:
        return "挑筋断骨"
    elif "Last Laugh" in str:
        return "两败俱伤"
    elif "Mists Convergence" in str:
        return "迷雾混流"
    elif "No Pain, No Gain" in str:
        return "祸福难料"
    elif "Outflanked" in str:
        return "腹背受敌"
    elif "Social Awkwardness" in str:
        return "社交障碍"
    elif "Stick Together" in str:
        return "团结一心"
    elif "Sugar Rush" in str:
        return "糖分冲击"
    elif "Toxic Sickness" in str:
        return "剧毒病症"
    elif "Toxic Trail" in str:
        return "剧毒尾迹"
    elif "Vengeance" in str:
        return "复仇"
    else:
        return "奇怪的错误"


def Replace_Profession(str):
    """
        替换职业
    """
    if "Weaver" in str:
        return "编织者"
    elif "Soulbeast" in str:
        return "魂兽师"
    elif "Catalyst" in str:
        return "元晶师"
    elif "Virtuoso" in str:
        return "灵刃术士"
    elif "Scrapper" in str:
        return "机械师"
    elif "Dragonhunter" in str:
        return "猎龙者"
    elif "Spellbreaker" in str:
        return "破法者"
    elif "Specter" in str:
        return "缚影者"
    elif "Firebrand" in str:
        return "燃火者"
    elif "Renegade" in str:
        return "龙魂使"
    elif "Bladesworn" in str:
        return "誓剑士"
    elif "Vindicator" in str:
        return "裁决者"
    elif "Reaper" in str:
        return "夺魂者"
    elif "Mechanist" in str:
        return "玉偃师"
    elif "Chronomancer" in str:
        return "时空术士"
    elif "Mirage" in str:
        return "幻象术士"
    elif "Scourge" in str:
        return "灾厄师"
    elif "Harbinger" in str:
        return "先驱者"
    elif "Holosmith" in str:
        return "全息师"
    elif "Druid" in str:
        return "德鲁伊"
    elif "Untamed" in str:
        return "狂兽师"
    elif "Daredevil" in str:
        return "独行侠"
    elif "Deadeye" in str:
        return "神枪手"
    elif "Willbender" in str:
        return "破峰者"
    elif "Herald" in str:
        return "预告者"
    elif "Berserker" in str:
        return "狂战士"
    elif "Tempest" in str:
        return "暴风使"
    else:
        return str


async def parse_environment():
    """
    进行CSS选择的函数，返回的是字典
    """
    # 标签的属性值中凡是出现空格的地方，在写CSS选择器的时候，都用.代替
    n_of_boss = await tab.querySelectorEval('div>h3', 'node => node.innerText')
    if n_of_boss == "Skorvald":
        return False
        # 排除非挑战模式的斯科瓦德
    date = await tab.querySelectorEval("div.footer>div", 'node => node.innerText')
    Mistlock_Instability1 = await tab.querySelectorEval("div>div>div>div img:nth-child(1)",
                                                        'node => node.dataset.originalTitle')
    Mistlock_Instability2 = await tab.querySelectorEval("div>div>div>div img:nth-child(2)",
                                                        'node => node.dataset.originalTitle')
    Mistlock_Instability3 = await tab.querySelectorEval("div>div>div>div img:nth-child(3)",
                                                        'node => node.dataset.originalTitle || null')
    battle_time = await tab.querySelectorEval("div>div>div>div div:nth-child(3)", 'node => node.innerText')
    team_total_damage = await tab.querySelectorEval("tfoot tr:nth-child(2) td:nth-child(5)", 'node => node.innerText')
    # team_ave_might = await tab.querySelectorEval("tfoot tr:nth-child(2) td:nth-child(5)", 'node => node.innerText')

    return {
        'BOSS名称': n_of_boss,
        '日期': date[6:16],
        "战斗时长": battle_time[6:],
        "团队总秒伤": team_total_damage[:-1],
        # "威能平均值": team_ave_might,
        '雾锁异变1': Replace_Mistlock_Instability(Mistlock_Instability1),
        '雾锁异变2': Replace_Mistlock_Instability(Mistlock_Instability2),
        '雾锁异变3': Replace_Mistlock_Instability(Mistlock_Instability3),
    }


async def parse_detail_of_player1():
    """
    进行CSS选择的函数，返回的是字典
    """
    # 标签的属性值中凡是出现空格的地方，在写CSS选择器的时候，都用.代替
    n_of_boss = await tab.querySelectorEval('div>h3', 'node => node.innerText')
    player1_name = await tab.querySelectorEval("tbody tr:nth-child(1) td:nth-child(4)", 'node => node.innerText')
    date = await tab.querySelectorEval("div.footer>div", 'node => node.innerText')
    DPS_Target = await tab.querySelectorEval("tbody tr:nth-child(1) td.sorting_1", 'node => node.innerText')
    DPS_Total = await tab.querySelectorEval("tbody tr:nth-child(1) td:nth-child(9)", 'node => node.innerText')
    profession = await tab.querySelectorEval("tbody tr:nth-child(1) td:nth-child(2) span", 'node => node.innerText')
    return {
        'BOSS名称': n_of_boss,
        '玩家1': player1_name[:-1],
        '日期': date[6:16],
        '单体': DPS_Target[:-1],
        '总体': DPS_Total[:-1],
        '职业': Replace_Profession(profession),
    }


async def parse_detail_of_player2():
    """
    进行CSS选择的函数，返回的是字典
    注意，有些日志可能会有错误，所以需要错误处理
    """
    # 标签的属性值中凡是出现空格的地方，在写CSS选择器的时候，都用.代替
    n_of_boss = await tab.querySelectorEval('div>h3', 'node => node.innerText')
    player2_name = await tab.querySelectorEval("tbody tr:nth-child(2) td:nth-child(4)", 'node => node.innerText')
    date = await tab.querySelectorEval("div.footer>div", 'node => node.innerText')
    DPS_Target = await tab.querySelectorEval("tbody tr:nth-child(2) td.sorting_1", 'node => node.innerText')
    DPS_Total = await tab.querySelectorEval("tbody tr:nth-child(2) td:nth-child(9)", 'node => node.innerText')
    profession = await tab.querySelectorEval("tbody tr:nth-child(2) td:nth-child(2) span", 'node => node.innerText')
    return {
        'BOSS名称': n_of_boss,
        '玩家2': player2_name[:-1],
        '日期': date[6:16],
        '单体': DPS_Target[:-1],
        '总体': DPS_Total[:-1],
        '职业': Replace_Profession(profession),
    }


async def parse_detail_of_player3():
    """
    进行CSS选择的函数，返回的是字典
    """
    # 标签的属性值中凡是出现空格的地方，在写CSS选择器的时候，都用.代替
    n_of_boss = await tab.querySelectorEval('div>h3', 'node => node.innerText')
    player3_name = await tab.querySelectorEval("tbody tr:nth-child(3) td:nth-child(4)", 'node => node.innerText')
    date = await tab.querySelectorEval("div.footer>div", 'node => node.innerText')
    DPS_Target = await tab.querySelectorEval("tbody tr:nth-child(3) td.sorting_1", 'node => node.innerText')
    DPS_Total = await tab.querySelectorEval("tbody tr:nth-child(3) td:nth-child(9)", 'node => node.innerText')
    profession = await tab.querySelectorEval("tbody tr:nth-child(3) td:nth-child(2) span", 'node => node.innerText')
    return {
        'BOSS名称': n_of_boss,
        '玩家3': player3_name[:-1],
        '日期': date[6:16],
        '单体': DPS_Target[:-1],
        '总体': DPS_Total[:-1],
        '职业': Replace_Profession(profession),
    }


async def parse_detail_of_player4():
    """
    进行CSS选择的函数，返回的是字典
    """
    # 标签的属性值中凡是出现空格的地方，在写CSS选择器的时候，都用.代替
    n_of_boss = await tab.querySelectorEval('div>h3', 'node => node.innerText')
    player3_name = await tab.querySelectorEval("tbody tr:nth-child(4) td:nth-child(4)", 'node => node.innerText')
    date = await tab.querySelectorEval("div.footer>div", 'node => node.innerText')
    DPS_Target = await tab.querySelectorEval("tbody tr:nth-child(4) td.sorting_1", 'node => node.innerText')
    DPS_Total = await tab.querySelectorEval("tbody tr:nth-child(4) td:nth-child(9)", 'node => node.innerText')
    profession = await tab.querySelectorEval("tbody tr:nth-child(4) td:nth-child(2) span", 'node => node.innerText')
    return {
        'BOSS名称': n_of_boss,
        '玩家4': player3_name[:-1],
        '日期': date[6:16],
        '单体': DPS_Target[:-1],
        '总体': DPS_Total[:-1],
        '职业': Replace_Profession(profession),
    }


async def parse_detail_of_player5():
    """
    进行CSS选择的函数，返回的是字典
    """
    # 标签的属性值中凡是出现空格的地方，在写CSS选择器的时候，都用.代替
    try:
        n_of_boss = await tab.querySelectorEval('div>h3', 'node => node.innerText')
        player3_name = await tab.querySelectorEval("tbody tr:nth-child(5) td:nth-child(4)", 'node => node.innerText')
        date = await tab.querySelectorEval("div.footer>div", 'node => node.innerText')
        DPS_Target = await tab.querySelectorEval("tbody tr:nth-child(5) td.sorting_1", 'node => node.innerText')
        DPS_Total = await tab.querySelectorEval("tbody tr:nth-child(5) td:nth-child(9)", 'node => node.innerText')
        profession = await tab.querySelectorEval("tbody tr:nth-child(5) td:nth-child(2) span", 'node => node.innerText')
    except:
        logging.error("An error occurred")
        return {
            'BOSS名称': None,
            '玩家5': None,
            '日期': None,
            '单体': None,
            '总体': None,
            '职业': None,
        }

    return {
        'BOSS名称': n_of_boss,
        '玩家5': player3_name[:-1],
        '日期': date[6:16],
        '单体': DPS_Target[:-1],
        '总体': DPS_Total[:-1],
        '职业': Replace_Profession(profession),
    }


# def Judge_DPS(boss, str_dps):
#     num_dps = int(str_dps)
#     for i in range(0, len(pass_line[0])):
#         if boss == pass_line[0][i]:
#             if num_dps < pass_line[1][i]:
#                 return False
#             else:
#                 return True


def save_as_json(list_of_dict, file_name):
    # with open(RESULTS_DIR, 'w', encoding='utf-8') as f:
    #     json.dump(list_of_dict, f)
    data_path = f'{RESULTS_DIR}/{file_name}.json'
    json.dump(list_of_dict, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False)


async def main():
    init_file()
    await init()
    for urls in LIST_OF_LOG_DIR:
        full_url = "file:///" + urls
        await scrape_page(full_url, ".text-left")
        detail_env = await parse_environment()
        if not detail_env:
            os.remove(urls)  # 删掉不是挑战的文件
            continue
        # detail_nums = await parse_detail_of_me()
        detail_nums1 = await parse_detail_of_player1()
        detail_nums2 = await parse_detail_of_player2()
        detail_nums3 = await parse_detail_of_player3()
        detail_nums4 = await parse_detail_of_player4()
        detail_nums5 = await parse_detail_of_player5()

        RESULT_ALL.append(detail_env)
        RESULT_ALL.append(detail_nums1)
        RESULT_ALL.append(detail_nums2)
        RESULT_ALL.append(detail_nums3)
        RESULT_ALL.append(detail_nums4)
        RESULT_ALL.append(detail_nums5)

    print(RESULT_ALL)
    save_as_json(RESULT_ALL, "所有结果")
    # print(Failure_List)
    # save_as_json(RESULT_ALL, "不及格")

    # plot_() #依然存在问题


asyncio.get_event_loop().run_until_complete(main())
