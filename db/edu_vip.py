'''数据库操作 之所以没有做成接口 是还不够完善 数据都是写死的
'''

import random
from datetime import datetime, timedelta
from importlib.metadata import metadata
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import Session
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import func
from sqlalchemy.types import Date
from api.vip import trigger_status


USER_ID = 11000000
VIP_SNS_ID = 0
VIP_EDU_ID = 31872

FUTURE_DATE_STR = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
PAST_DATE_STR = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')


db_sns = 'mysql+pymysql://root:FE4v2MB7cv5F3rBT@10.25.98.5:3306/sns'
db_vip = 'mysql+pymysql://root:FE4v2MB7cv5F3rBT@10.25.21.22:3306/vip_center'

engine_sns = create_engine(db_sns, echo=True)
engine_vip_center = create_engine(db_vip, echo=True)

# meta = MetaData()

def f1():    
    meta = MetaData()
    apply_download_article_video_log = Table('ts_apply_download_article_video_log', meta, autoload_with=engine_sns)
    conn = engine_sns.connect()
    ins = apply_download_article_video_log.insert().values(user_id=10001000, article_id=11297151, created_time='2022-08-08 00:00:00', updated_time='2022-08-08 00:00:00')
    conn.execute(ins)

# class ApplyDownloadArticleVideoLog(Base):
#     __tablename__ = 'ts_apply_download_article_video_log'

def test_f():
    articles_10858839 = ['11291752','11291745','11291733','11291723','11291722','11291695','11291694','11291690','11291689','11291688','11291687','11291686','11291618','11291617','11291583','11291582','11291581','11291580','11291570','11291569','11291568','11291565','11291560','11291543','11291542','11291541','11291540','11291535','11291534','11291533','11291532','11291525','11291520','11291519','11291518','11291517','11291516','11291515','11291513','11291512','10879034','10878982','10878981','10878980','10878979','10878977','10878973','10878972','10878971','10878947','10876490','10874996','10874520','10871384','10871273','10869756','10867924','10866080','10866002','10864489','10852829','10852540','10850393','10850230','10850218','10844820','10844351','10833528','10832276','10832033','10829957','10828744','10823132','10822119','10817423','10817306','10816356','10802185','10801967','10800299','10781375','10781185','10780126','10780090','10773368','10767062','10766699','10766436','10764466','10760714','10760373','10759040','10754413','10751470','10749956','10748889','10747830','10745152','10734705','10733828','10732742','10730762','10730234','10730148','10728904','10728563','10728045','10727955','10726622','10726301','10723500','10722655','10722475','10722272','10720435','10719843','10719835','10719829','10719824','10719811','10719803','10719798','10719784','10719779','10719777','10719775','10719768','10719767','10719763','10719757','10719748','10719735','10719733','10719732','10719704','10719698','10719692','10719689','10719684','10719682','10719680','10719673','10719671','10719664','10719654','10719653','10719651','10719650','10719647','10719639','10719625','10719618','10719613','10719612','10719601','10719599','10719598','10719596','10719581','10719576','10719569','10719568','10719562','10719546','10719537','10719522','10719510','10719503','10719498','10719497','10719491','10719485','10719463','10719457','10719431','10719420','10719416','10719409','10719401','10719377','10719368','10719367','10719347','10719346','10719344','10719343','10719329','10719328','10719324','10719320','10719316','10719307','10719301','10719283','10719242','10719234','10719231','10719229','10719202','10719195','10719194','10719184','10719168','10719167','10719136','10719125','10719119','10719104','10719092','10719080','10719069','10719063','10719059','10719049','10719036','10719031','10719022','10719012','10718999','10718979','10718972','10718962','10718958','10718928','10718927','10718915','10718877','10718863','10718817','10718811','10718793','10718782','10718774','10718763','10718753','10718752','10718747','10718745','10718737','10718734','10718722','10718701','10718690','10718683','10718682','10718653','10718646','10718644','10718637','10718634','10718615','10718609','10718598','10718597','10718595','10718586','10718585','10718581','10718580','10718564','10718560','10718546','10718527','10718515','10718507','10718503','10718494','10718485','10718483','10718481','10718471','10718469','10718461','10718456','10718449','10718443','10718442','10718440','10718428','10718422','10718415','10718401','10718396','10718393','10718388','10718381','10718364','10718362','10718356','10718350','10718341','10718340','10718334','10718329','10718319','10718313','10718307','10718303','10718299','10718296',]
    users = ['11248398','10858927','10418526','10859029','10521874','10863753','10472864','10038308','10859947','10147296','10082663','10863755','10349931','11248448','10607647','10356001','10078195','10002017','10874561','10136256','10020375','10955704','10859008','10064482','11354206','10213793','10256301','10053067','10394697','10881640','10979047','11248462','10128941','11174874','10324158','10355771','11348137','10830607','10365420','10508553','10323446','10197910','10393716','10926274','10858924','10304448','10033980','10936616','10001910','10012938','10004722','10094985','10257627','10013255','10012438','10030996','10667654','10017617','10147370','11185923','10080857','10001931','10000894','10039292','10862801','10089459','10384554','10090144','10006837','10372923','10859962','10412475','10004101','11415719','10002713','10046567','11073561','10269751','10365351','10010354','10002743','10515721','10608656','10549785','10664134','10004341','10084427','10505120','10133882','10353548','10744676','10862414','10287153','10981204','10316553','10001971','10241390','10657695','11342234','10015729','10295594','10581068','10027957','10219825','10357476','10061939','10094586','10265312','10247496','10275487','10006283','10001320','10922434','10001797','10987832','10125697','10220767','10040348','10569888','10000904','10244266','10011838','10010631','10624004','10313950','10511990','10109754','10688102','10092067','10180673','10003256','10298066','10927144','10091852','10030779','10042758','11341590','10211947','10001822','11459181','10295203','10542698','10041908','10789001','10001276','10547443','10029222','10825168','11416011','10449979','10010180','10715434','10687223','10249630','10008750','10580225','10604082','10005592','10038892','11210068','10027818','10057973','10107660','10742034','10638547','10394590','10264351','10765660','10014989','10730136','10543862','10391576','10276469','10867390','10234373','10665079','10020127','10059773','10837997','10000560','10941964','10168338','10670391','11222500','10874865','10849714','10695604','10118885','10002622','10010342','10001273','10218008','10545032','10007818','10006618','10610956','10977211','10541328','10908910','10718572','10066589','10553920','10017163','10608910','10612231','10101057','10575537','10777196','10974065','10187898','10875581','10007472','10523951','10447414','10304161','10681578','10323879','10765406','10689066','10450407','10347729','11047167','10028046','10001917','10072226','10357540','10041555','10000719','10003314','10299797','11341970','11013091','10983475','10013140','10211742','10315870','10218125','10134052','10798161','10035770','10069969','10015221','10370428','10650342','10010431','10010920','10047770','10200545','10070752','10859940','10026682','11370742','10352866','10427278','10121463','10537541','10632772','10190328','10009540','10803830','10887456','10001068','10830305','10018075','10621353','10731002','10204334','10174024','10003140','10512139','10588991','10264439','10400695','10835183','10003344','10548182','10671429','10255348','10732841','10412276','10494733','10001253','10320586','10081952','10008167','10733106','10522923','10878254','10407408','10812195','10335661','10066706','10006985','10034849','10778844','10431719','10430270','11042178','10653541',]
    
    meta = MetaData()

    # Base = automap_base()
    # Base.prepare(autoload_with=engine)
    # print([c for c in Base.classes])

    meta.reflect(engine_sns, only=['ts_apply_download_article_video_log', 'ts_article'])
    Base = automap_base(metadata=meta)
    Base.prepare()
    
    ApplyDownloadArticleVideoLog = Base.classes.ts_apply_download_article_video_log
    Articles = Base.classes.ts_article
    
    session = Session(engine_sns)
    
    authors = [
        # 10080857, 
        # 10608656, 
        # 10011838, 
        10265312
    ]
    logs = []
    # dt = datetime.now().strftime('2022-08-29 %H:%M:%S')
    dt =  '2022-10-28 10:00:00'
    print(dt)
    # for author in authors:
    #     articles = session.query(Articles).filter(Articles.userid==author, Articles.isshow==1).order_by(text('articleid')).limit(5).all()
    #     for a in articles:
    #         for user in random.choices(users, k=random.randint(0, 100)):
    #             logs.append(ApplyDownloadArticleVideoLog(user_id=user, article_id=a.articleid, created_time=dt, updated_time=dt))
    articles = (10221922, 11297115, 11296279)
    for a in articles:
        for i in range(10001000, 10001100):
            logs.append(ApplyDownloadArticleVideoLog(user_id=i, article_id=a, created_time=dt, updated_time=dt))

    # session.add_all(logs)
    session.bulk_save_objects(logs)
    session.commit()

def get_table(table='vip', engine=engine_vip_center):
    '''todo: 多个数据库
    '''
    meta = MetaData()

    meta.reflect(engine, only=[table])
    Base = automap_base(metadata=meta)
    Base.prepare()
    
    Table = getattr(Base.classes, table)
    return Table

def update_expired_date(vip_id, end:Date|str, start:Date|str='2022-02-02',vip_flag=1):
    '''
    :param vip_flag:1 vip, 3 svip, 7 blackdiamond, 8 edu_quarter_vip, 16 edu_year_vip
    '''
    # 修改vip表数据
    Vip = get_table('vip')
    with Session(engine_vip_center) as sess:
        
        v = sess.get(Vip, vip_id)
        v.start = start
        v.end = end
        v.vip_flag = vip_flag
        sess.commit()
   
def test_meta():
    '''todo:
    1 meta.reflect: schema, for meta.tables['schema.table_name']
    2 MetaDate(engine): if reflect all tables
    3 Session = sessionmaker(engine), Session()
    4 with Session() as s, s.begin():
    5 Table 由 engine 反射得来, 为什么 session还需要binds才知道查哪个数据库?
    '''

    meta = MetaData()
    meta.reflect(engine_vip_center, only=['vip'])
    meta.reflect(engine_sns, only=['ts_user_info'])
    # Vip = meta.tables['vip']
    # UserInfo = meta.tables['ts_user_info']
    Vip = Table('vip', meta, autoload_with=engine_vip_center)
    UserInfo = Table('ts_user_info', meta, autoload_with=engine_sns)
    binds = {
        Vip: engine_vip_center,
        UserInfo: engine_sns
    }
    with Session(binds=binds) as s:
        # vip = s.get(Vip, 1)
        vip = s.query(Vip).filter_by(id=1).one()
        user = s.query(UserInfo).filter_by(userid=10000010).one()
    print(type(vip), dir(vip), vip.keys(), vip.created_at)
    print(user)

    # meta.reflect(engine_sns, schema='sns')
    # UserInfo = meta.tables['sns.ts_user_info']
