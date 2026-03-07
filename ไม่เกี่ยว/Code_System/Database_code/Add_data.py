import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- 1. ตั้งค่าการเชื่อมต่อ ---
db_key = os.getenv("DB_KEY")
client = MongoClient(db_key)
db = client['Knowledge_hub']
collection = db['Fig_data']

print("กำลังโหลดโมเดล...")
model = SentenceTransformer('BAAI/bge-m3')

# --- 2. นำข้อมูลของคุณมาใส่ในตัวแปร List ---
data_to_insert = [
    {"text": "โครงสร้างพื้นฐานแบบบริการ (Infrastructure as a Service: IaaS)ผู้ให้บริการจะจัดเตรียมเฉพาะทรัพยากรด้านฮาร์ดแวร์ เช่น เซิร์ฟเวอร์ หน่วยประมวลผล พื้นที่จัดเก็บข้อมูล และเครือข่าย ในขณะที่ผู้ใช้มีหน้าที่ดูแลระบบปฏิบัติการ การติดตั้งซอฟต์แวร์ และการดูแลแอปพลิเคชันต่าง ๆ ที่อยู่บนระบบนั้น ตัวอย่างของ IaaS ได้แก่ Amazon EC2, Microsoft Azure Virtual Machines และ Google Compute Engine", 
"page":"13", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26bb00399eef961e/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"2.Infrastructure as a Service_หน้าที่6.png", 
"pic_number":"2"},


{"text": "ผู้ให้บริการระบบคลาวด์รายใหญ่ที่สุด (Largest Cloud Service Providers)ผู้ให้บริการระบบคลาวด์ (Cloud Service Providers: CSPs) คือองค์กรที่ให้บริการทรัพยากรคอมพิวเตอร์ผ่านระบบคลาวด์ในรูปแบบการสมัครใช้งาน (Subscription-Based) โดยทรัพยากรที่ให้บริการอาจอยู่ในระดับโครงสร้างพื้นฐาน เช่น ฮาร์ดแวร์และเครื่องเสมือนในรูปแบบ Infrastructure as a Service (IaaS) หรืออยู่ในรูปแบบของซอฟต์แวร์สำเร็จรูปที่ให้บริการผ่านระบบคลาวด์ เช่น Microsoft 365 ซึ่งอยู่ในกลุ่ม Software as a Service (SaaS)", 
"page":"19", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26be003d9120f736/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"3.Software as a Service (SaaS)_หน้าที่12.png", 
"pic_number":"3"},


{"text": "บทบาทของผู้ให้บริการคลาวด์แบบมีการจัดการ (Role of Cloud Managed Service Providers: MSPs)การดำเนินงานด้านระบบคลาวด์ภายในองค์กร โดยเฉพาะในองค์กรขนาดเล็กและขนาดกลาง อาจประสบความท้าทายในการจัดหาบุคลากรที่มีความเชี่ยวชาญครอบคลุมทุกด้านของเทคโนโลยีคลาวด์ ซึ่งมีความซับซ้อนและมีการเปลี่ยนแปลงอย่างรวดเร็ว เพื่อแก้ไขปัญหาดังกล่าว องค์กรสามารถเลือกใช้บริการจากผู้ให้บริการภายนอกที่เรียกว่า ผู้ให้บริการระบบคลาวด์แบบมีการจัดการ (Managed Service Providers: MSPs) ซึ่งเป็นบุคคลหรือนิติบุคคลอิสระที่ไม่ขึ้นตรงกับผู้ให้บริการคลาวด์รายใหญ่ (Cloud Service Providers: CSPs) โดยองค์กรสามารถว่าจ้าง MSP เหล่านี้ให้ช่วยดำเนินงานด้านต่าง ๆ เช่น การออกแบบระบบคลาวด์ การโยกย้ายระบบ (Migration) การติดตั้งระบบ (Deployment) ตลอดจนการบริหารจัดการและดูแลระบบคลาวด์อย่างต่อเนื่อง ผู้ให้บริการคลาวด์รายใหญ่บางราย เช่น Amazon Web Services (AWS) ก็มีบริการ AWS Managed Services ซึ่งเป็นการให้บริการจัดการระบบภายในแพลตฟอร์มของตนเอง การใช้บริการ MSP มีแนวโน้มช่วยให้องค์กรสามารถลดต้นทุนในการดำเนินงาน (Operating Expenditures: OpEx) และเพิ่มประสิทธิภาพโดยรวมของระบบได้อย่างชัดเจน", 
"page":"21", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26c4000e71371a87/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"4.Role of Cloud Managed Service Providers_หน้าที่14.png", 
"pic_number":"4"},


{"text": "โมเดลความรับผิดชอบร่วมกัน (Shared Responsibility Model)ในระบบคลาวด์ การรักษาความมั่นคงปลอดภัยไม่ได้เป็นหน้าที่ของฝ่ายใดฝ่ายหนึ่งโดยสมบูรณ์ แต่เป็นรูปแบบของ ความรับผิดชอบร่วมกัน (Shared Responsibility Model) ระหว่างผู้ให้บริการระบบคลาวด์ (Cloud Service Provider: CSP) และผู้ใช้งานระบบคลาวด์ (Cloud Consumer) ซึ่งแต่ละฝ่ายจะมีบทบาทหน้าที่เฉพาะในด้านการรักษาความปลอดภัยของระบบ โดยทั่วไป ผู้ให้บริการคลาวด์จะรับผิดชอบด้านความมั่นคงปลอดภัยทางกายภาพของศูนย์ข้อมูล เช่น การควบคุมการเข้าถึงทางกายภาพของอาคาร การรักษาความปลอดภัยของเครือข่ายโครงสร้างพื้นฐาน และการแยกข้อมูลของผู้ใช้แต่ละรายไม่ให้ปะปนกัน ในขณะที่ผู้ใช้งานระบบคลาวด์จะต้องรับผิดชอบในส่วนของการรักษาความปลอดภัยของข้อมูลของตนเอง รวมถึงการควบคุมการเข้าถึงของผู้ใช้ การกำหนดสิทธิ์การใช้งานข้อมูล และการเข้ารหัสข้อมูล (Encryption) เพื่อป้องกันการเข้าถึงโดยไม่ได้รับอนุญาต", 
"page":"23", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26c800096fdb847c/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"5.Shared Responsibility Model_หน้าที่16.png", 
"pic_number":"5"},


{"text": "ทบทวนแนวคิดเกี่ยวกับเวอร์ชวลไลเซชัน (Virtualization Review) เวอร์ชวลไลเซชัน (Virtualization) ถือเป็นแนวคิดพื้นฐานที่สำคัญของระบบคลาวด์ โดยเป็นเทคโนโลยีที่ช่วยแยกระบบปฏิบัติการ บริการ และแอปพลิเคชัน ออกจากข้อจำกัดของฮาร์ดแวร์จริง ทำให้สามารถนำไปใช้งานบนแพลตฟอร์มที่จัดสรรทรัพยากรด้านการประมวลผล พื้นที่จัดเก็บข้อมูล และเครือข่ายได้อย่างยืดหยุ่น ระบบคลาวด์จะไม่สามารถเกิดขึ้นได้หากปราศจากเทคโนโลยีเวอร์ชวลไลเซชันนี้ ปัจจุบันมีโซลูชันด้านเวอร์ชวลไลเซชันที่หลากหลาย ไม่ว่าจะเป็น เครื่องเสมือน (Virtual Machines: VMs), คอนเทนเนอร์ (Containers) และ เครือข่ายเสมือน (Virtual Networks) ซึ่งต่างก็มีบทบาทเฉพาะในการออกแบบระบบคลาวด์", 
"page":"25", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26cc000e1694fcae/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"6.Virtualization Review_หน้าที่18.png", 
"pic_number":"6"},


{"text": "การค้นหาบริการ (Service Discovery) ในสถาปัตยกรรมไมโครเซอร์วิส (Microservices Architecture) แต่ละบริการจะทำงานอย่างอิสระและให้ฟังก์ชันเฉพาะของตนเอง เมื่อนำหลายบริการมาทำงานร่วมกัน จึงจะเกิดเป็นแอปพลิเคชันที่สมบูรณ์ หนึ่งในข้อได้เปรียบสำคัญของระบบคลาวด์คือ ความสามารถในการปรับขนาด (Scalability) ซึ่งทำให้จำนวนของไมโครเซอร์วิสสามารถเพิ่มหรือลดลงได้ตามภาระงานแบบไดนามิก", 
"page":"42", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26cf000fd5f2c76c/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"7.Service Discovery_หน้าที่35.png", 
"pic_number":"7"},


{"text": "Function Chain (โซ่ฟังก์ชันแบบเรียงลำดับ) ฟังก์ชันแต่ละตัวทำงานต่อเนื่องกันตามลำดับทีละขั้นตอน ตัวอย่างเช่น: ฟังก์ชัน A → B → C", 
"page":"43", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26d20033d00b7cf4/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"8.Function Chain_หน้าที่36.png", 
"pic_number":"8"},


{"text": "Fan-out / Fan-in ฟังก์ชันหลายตัวสามารถทำงานพร้อมกันได้ (Fan-out) ผลลัพธ์จากฟังก์ชันเหล่านั้นจะถูกรวมเข้าด้วยกันในภายหลัง (Fan-in) ตัวอย่างเช่น: A → [B, C] ทำงานพร้อมกัน แล้วรวมผลลัพธ์กลับสู่ฟังก์ชัน D รูปแบบการทำงานลักษณะนี้ช่วยเพิ่มความเร็ว ความยืดหยุ่น และประสิทธิภาพในการจัดการภาระงาน (Load) ในสภาพแวดล้อมแบบ Cloud-native และ Serverless", 
"page":"43", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26d5003842cbfeae/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"9.Fan-outFan-in_หน้าที่36.png", 
"pic_number":"9"},


{"text": "องค์ประกอบของระบบคลาวด์ (Cloud Components) ระบบบริการคลาวด์ประกอบด้วยองค์ประกอบหลัก 3 ส่วน ได้แก่ 1. แพลตฟอร์มของผู้ใช้งาน (Client Platform) คืออุปกรณ์หรือระบบที่ผู้ใช้นำมาใช้เพื่อเข้าถึงบริการคลาวด์ เช่น คอมพิวเตอร์ แท็บเล็ต สมาร์ตโฟน หรืออุปกรณ์ Internet of Things (IoT) 2. ศูนย์ข้อมูลของผู้ให้บริการคลาวด์ (Data Center of Cloud Service Provider) เป็นสถานที่ที่ใช้โฮสต์บริการคลาวด์ทั้งหมด โดยมีความสามารถในการเข้าถึงพลังงานและอินเทอร์เน็ตที่เชื่อถือได้ มีระบบสำรอง (Redundancy) และมีมาตรการด้านความปลอดภัยทางกายภาพในระดับสูง 3. เครือข่ายที่เชื่อมต่อ (Network Connection) เป็นเส้นทางที่เชื่อมโยงระหว่างศูนย์ข้อมูลของผู้ให้บริการคลาวด์กับอุปกรณ์ของผู้ใช้งาน ซึ่งอาจเป็นเครือข่ายภายในองค์กร อินเทอร์เน็ต หรือเครือข่ายโทรศัพท์มือถือ", 
"page":"45", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26da00029f7eee8c/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"10.Cloud Components_หน้าที่38.png", 
"pic_number":"10"},


{"text": "คลาวด์สาธารณะ (Public Cloud) คลาวด์สาธารณะเป็นบริการคลาวด์ที่องค์กรต่าง ๆ ซึ่งไม่เกี่ยวข้องกันสามารถเข้ามาใช้งานร่วมกันได้ ผู้ให้บริการคลาวด์ (Cloud Service Provider: CSP) เช่น Amazon, Microsoft หรือ Google จะเปิดให้ลูกค้าเข้าถึงทรัพยากรในศูนย์ข้อมูลของตนผ่านระบบการสมัครใช้งานแบบรายเดือนหรือรายปี ลูกค้าที่ใช้งานคลาวด์สาธารณะจะใช้ทรัพยากรร่วมกับผู้ใช้รายอื่น ซึ่งระบบของผู้ให้บริการจะบริหารจัดการและจัดสรรทรัพยากรให้โดยอัตโนมัติตามปริมาณการใช้งานจริงในขณะนั้น ผู้ใช้งานจึงไม่จำเป็นต้องทราบว่าข้อมูลของตนถูกเก็บไว้ที่ตำแหน่งใดภายในศูนย์ข้อมูล รูปแบบคลาวด์นี้ถือเป็นภาพจำของคนทั่วไปเมื่อนึกถึง “คลาวด์คอมพิวติ้ง” โดยเฉพาะในกรณีของธุรกิจที่ต้องการความยืดหยุ่นและต้องการลดต้นทุนด้านโครงสร้างพื้นฐาน", 
"page":"46", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26dd003509a15bb1/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"11.Public Cloud_หน้าที่39.png", 
"pic_number":"11"},


{"text": "คลาวด์ส่วนตัว (Private Cloud) คลาวด์ส่วนตัวเป็นรูปแบบการให้บริการคลาวด์ที่จำกัดการใช้งานเฉพาะองค์กรที่เป็นเจ้าของระบบเท่านั้น โดยองค์กรจะลงทุนสร้างศูนย์ข้อมูล (Data Center) ภายในบริษัทของตนเอง พร้อมทั้งใช้เทคโนโลยีการจำลองเสมือน (Virtualization) เพื่อให้สามารถจัดสรรทรัพยากรด้านคอมพิวติ้งได้อย่างมีประสิทธิภาพ บริการคลาวด์ในรูปแบบนี้จะถูกนำมาให้บริการแก่ผู้ใช้งานภายในองค์กรผ่านแคตตาล็อกของบริการ (Service Catalog) ซึ่งผู้ใช้งานภายในสามารถเข้าถึงและใช้งานทรัพยากรต่าง ๆ ได้ตามสิทธิ์ที่กำหนด", 
"page":"48", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26e1003e79827003/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"12.Private Cloud_หน้าที่41.png", 
"pic_number":"12"},


{"text": "คลาวด์ชุมชน (Community Cloud) คลาวด์ชุมชนเป็นรูปแบบของระบบคลาวด์ที่ถูกออกแบบมาเพื่อให้บริการเฉพาะกลุ่มขององค์กรที่มีลักษณะการดำเนินธุรกิจหรือข้อกำหนดด้านความปลอดภัยที่คล้ายคลึงกัน โดยสมาชิกในกลุ่มนี้เท่านั้นที่สามารถเข้าถึงทรัพยากรของระบบคลาวด์ได้ ในขณะที่บุคคลภายนอกจะไม่สามารถใช้งานร่วมได้ การจัดการระบบคลาวด์ชุมชนอาจดำเนินการโดยองค์กรใดองค์กรหนึ่งภายในกลุ่ม หรืออาจเป็นการร่วมกันบริหารจัดการของหลายองค์กร หรืออาจว่าจ้างบุคคลหรือหน่วยงานภายนอกให้เป็นผู้ดูแลระบบก็ได้", 
"page":"49", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26e5000e50a9a427/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"13.Community Cloud_หน้าที่42.png", 
"pic_number":"13"},


{"text": "คลาวด์แบบผสม (Hybrid Cloud) คลาวด์แบบผสมคือการผสมผสานรูปแบบการให้บริการคลาวด์ทั้งแบบสาธารณะ (Public Cloud), ส่วนตัว (Private Cloud) และ/หรือคลาวด์ชุมชน (Community Cloud) เข้าด้วยกัน เพื่อให้สามารถใช้งานได้อย่างยืดหยุ่นและตรงตามความต้องการขององค์กร ตัวอย่างเช่น องค์กรหนึ่งอาจใช้บริการบางส่วนผ่านระบบคลาวด์สาธารณะของผู้ให้บริการ (Cloud Service Provider: CSP) เช่น Amazon Web Services, Microsoft Azure หรือ Google Cloud สำหรับการเก็บข้อมูลทั่วไปหรือให้บริการเว็บแอปพลิเคชันที่ไม่ต้องการความปลอดภัยสูง ในขณะเดียวกัน องค์กรอาจเก็บข้อมูลที่มีความอ่อนไหวไว้ภายในศูนย์ข้อมูลของตนเองผ่านระบบคลาวด์ส่วนตัว (Private Cloud) เพื่อให้สามารถควบคุมความปลอดภัยและการเข้าถึงข้อมูลได้อย่างมีประสิทธิภาพ", 
"page":"51", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26e900072144046f/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"14.Hybrid Cloud_หน้าที่44.png", 
"pic_number":"14"},


{"text": "มัลติคลาวด์ (Multi-Cloud) มัลติคลาวด์คือแนวทางที่องค์กรเลือกใช้งานบริการคลาวด์จากผู้ให้บริการมากกว่าหนึ่งรายพร้อมกัน เพื่อเพิ่มความยืดหยุ่นในการใช้งาน ลดความเสี่ยงจากการพึ่งพาผู้ให้บริการรายเดียว และสามารถเลือกใช้บริการที่เหมาะสมที่สุดจากแต่ละแพลตฟอร์ม โดยทั่วไปผู้ให้บริการที่องค์กรนิยมใช้งานร่วมกันมักเป็นผู้ให้บริการคลาวด์สาธารณะรายใหญ่ เช่น Amazon Web Services (AWS), Microsoft Azure และ Google Cloud", 
"page":"52", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26ec00050d87ec82/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"15.Multi-cloud_หน้า45.png", 
"pic_number":"15"},


{"text": "การแยกสภาพแวดล้อมทางไอที (Separate IT Environments) ผู้ดูแลระบบมักจะแยกสภาพแวดล้อมทางไอทีออกจากกัน เพื่อแยกระบบที่ใช้งานจริง (Production) ออกจากกระบวนการพัฒนา (Development) ตัวอย่างที่พบบ่อย ได้แก่ สภาพแวดล้อมการพัฒนา (Development Environment), สภาพแวดล้อมทดสอบก่อนใช้งานจริงหรือสเตจจิง (Staging Environment) และสภาพแวดล้อมการใช้งานจริง (Production Environment) ซึ่งแต่ละสภาพแวดล้อมอาจมีรูปแบบแตกต่างกันไปตามลักษณะขององค์กร และใช้ทรัพยากรไม่เท่ากัน (ส่งผลต่อค่าใช้จ่ายโดยตรง)", 
"page":"57", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26ef0004160da9ae/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"16.Separate IT Environments_หน้า50.png", 
"pic_number":"16"},


{"text": "รูปแบบการเผยแพร่แอปพลิเคชัน (Application Release Models) มีรูปแบบการเผยแพร่และปรับใช้ซอฟต์แวร์หลายประเภทที่ช่วยให้ผู้ดูแลระบบสามารถติดตั้งและจัดการแอปพลิเคชันได้อย่างถูกต้องและมีประสิทธิภาพ ไม่ได้จำกัดเฉพาะแอปพลิเคชันสำหรับผู้ใช้งานทั่วไป เช่น ชุดโปรแกรมสำนักงานหรือเว็บเบราว์เซอร์เท่านั้น แต่ยังครอบคลุมไปถึงแอปพลิเคชันระดับองค์กร เช่น ฐานข้อมูล แอปพลิเคชันเว็บ และบริการเครือข่าย", 
"page":"58", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26f30000d6e6e04a/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"17.Application Release Models_หน้า51.png", 
"pic_number":"17"},


{"text": "กลยุทธ์การปรับใช้แบบ Blue-Green (Blue-Green Deployment Strategy) แนวทาง Blue-Green Deployment เป็นรูปแบบหนึ่งของการแยกสภาพแวดล้อมการพัฒนา ทดสอบ และใช้งานจริงออกจากกัน โดยจะมีการสร้างสภาพแวดล้อมที่เหมือนกันสองชุด คือ “Blue” และ “Green” ซึ่งในขณะใดขณะหนึ่งจะมีเพียงชุดเดียวเท่านั้นที่ทำหน้าที่เป็นสภาพแวดล้อมการผลิต (Production)", 
"page":"60", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26f80030b4234b57/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"18. Blue-Green Deployment Strategy_หน้า53.png", 
"pic_number":"18"},


{"text": "กลยุทธ์การปรับใช้แบบ Canary (Canary Deployment Strategy) Canary Deployment เป็นแนวทางที่คล้ายกับ Blue-Green แต่มีความแตกต่างตรงที่ผู้ใช้งานจะถูกย้ายจากเวอร์ชันเดิมไปยังเวอร์ชันใหม่อย่างค่อยเป็นค่อยไป ไม่ใช่ทั้งหมดในคราวเดียว โดยในระยะแรกจะมีเพียงกลุ่มผู้ใช้จำนวนน้อยที่ได้รับการเข้าถึงซอฟต์แวร์เวอร์ชันใหม่ เพื่อทำการทดสอบและให้ข้อเสนอแนะ ก่อนที่จะขยายการใช้งานไปยังผู้ใช้ทั้งหมด", 
"page":"61", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac26fd001355ce45a1/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"19.Canary Deployment Strategy_หน้า54.png", 
"pic_number":"19"},


{"text": "การย้ายข้อมูลขึ้นคลาวด์ (Migrate Data to the Cloud) ผู้ให้บริการคลาวด์แต่ละรายมีเครื่องมือหลากหลายสำหรับการย้ายข้อมูลขนาดใหญ่จากระบบภายในองค์กรไปยังคลาวด์ โดยแบ่งออกเป็นสองแนวทางหลัก ได้แก่ การถ่ายโอนผ่านเครือข่ายอินเทอร์เน็ต (รวมถึงการเชื่อมต่อโดยตรงที่มีความปลอดภัย) และการถ่ายโอนแบบออฟไลน์ผ่านอุปกรณ์จัดเก็บข้อมูลทางกายภาพ ตัวอย่างการเชื่อมต่อโดยตรงและเครื่องมือจากผู้ให้บริการคลาวด์", 
"page":"90", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2702001c542ec06f/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"20.Migrate Data to the Cloud_หน้า83.png", 
"pic_number":"20"},


{"text": "AWS M4 Instances (กลุ่ม General-Purpose): m4.large: vCPU = 2, RAM = 8 GiB, ใช้ EBS เท่านั้น, แบนด์วิดท์ของ EBS = 450 Mbps m4.xlarge: vCPU = 4, RAM = 16 GiB, ใช้ EBS เท่านั้น, แบนด์วิดท์ของ EBS = 750 Mbps", 
"page":"96", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2706001dd0891edc/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"21.AWS M4 Instances_หน้า89.png", 
"pic_number":"21"},


{"text": "AWS D2 Instances (กลุ่ม Storage-Optimized): d2.xlarge: vCPU = 4, RAM = 30.5 GiB, พื้นที่จัดเก็บ = 3×2 TB HDD d2.2xlarge: vCPU = 8, RAM = 61 GiB, พื้นที่จัดเก็บ = 6×2 TB HDD", 
"page":"96", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac271c0004b5937c19/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"22.AWS D2 Instances_หน้า89.png", 
"pic_number":"22"},


{"text": "การติดแท็กทรัพยากร (Resource Tagging) การแท็กหมายถึงการกำหนดป้ายกำกับ (Labels) ให้กับทรัพยากรต่าง ๆ ในระบบคลาวด์ โดยไม่ควรสับสนกับการใช้แท็กเพื่อจุดประสงค์ด้านความปลอดภัย เช่น ป้ายกำกับเพื่อควบคุมการเข้าถึง เพราะแท็กในบริบทนี้ถูกใช้เพื่อการกำกับดูแล (Governance) และการจัดการต้นทุน (Cost Management) แท็กจะถูกนำมาใช้ในการสร้างรายงานค่าใช้จ่ายและการใช้งานในเครื่องมืออย่างเช่น AWS Billing and Cost Management Console", 
"page":"113", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2720001f75f3ce95/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"23. Resource Tagging_หน้า106.png", 
"pic_number":"23"},


{"text": "การปรับขนาดให้เหมาะสม (Rightsizing) บริการคลาวด์ช่วยให้การปรับแต่งทรัพยากรคอมพิวต์ให้เหมาะสมกับปริมาณงาน (Workload) เป็นเรื่องง่าย ซึ่งในอดีตเมื่อใช้เซิร์ฟเวอร์แบบดั้งเดิม การจัดสรรทรัพยากร เช่น หน่วยประมวลผลกลาง (CPU), หน่วยความจำ (Memory), ที่เก็บข้อมูล (Storage) และเครือข่าย (Network) มักเป็นแบบตายตัว ผู้ดูแลระบบจึงมักเลือกสเปกสูงเกินจริงเพื่อรองรับการเติบโตในอนาคต ส่งผลให้เกิดการใช้ทรัพยากรไม่เต็มประสิทธิภาพและสิ้นเปลืองงบประมาณโดยไม่จำเป็น", 
"page":"114", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac27230030b4f105a8/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"24.Rightsizing_หน้า107.png", 
"pic_number":"24"},

{"text": "การจำลองระบบแบบสแตนด์อโลน (Stand-alone Virtualization) การจำลองระบบแบบสแตนด์อโลนหมายถึงการกำหนดค่าของเครื่องเสมือน (VM) ให้เหมือนกับเครื่องเซิร์ฟเวอร์จริง (Physical System) โดยผู้ดูแลระบบจะต้องดำเนินการจัดสรรทรัพยากร เช่น หน่วยความจำ (Memory), ที่จัดเก็บข้อมูล (Storage), หน่วยประมวลผล (CPU) และเครือข่าย (Networking) ให้กับ VM เพื่อให้สามารถเชื่อมต่อและทำงานบนเครือข่ายได้เช่นเดียวกับเซิร์ฟเวอร์ Linux หรือเวิร์กสเตชันทั่วไป", 
"page":"119", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2727001803732562/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"25.Stand-Alone Virtualization_หน้า112.png", 
"pic_number":"25"},


{"text": "แม่แบบไฟล์การกำหนดค่าเครื่องเสมือน (Virtual Machine Configuration File Templates) ไฟล์การกำหนดค่า (Configuration Files) คือไฟล์ที่ใช้กำหนดพารามิเตอร์ต่าง ๆ ของเครื่องเสมือน (VM) โดยระบุรายละเอียดเกี่ยวกับการจัดสรรฮาร์ดแวร์ทั้งหมด เช่น • ข้อมูลหน่วยประมวลผลกลาง (CPU) • ปริมาณหน่วยความจำ (RAM) • ตัวเลือกเครือข่าย (Network Options) • ประเภทและขนาดของที่จัดเก็บข้อมูล (Storage)", 
"page":"121", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac272c00022927353c/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"26.Virtual Machine Configuration File Templates_หน้า114.png", 
"pic_number":"26"},


{"text": "การจำลองระบบแบบคลัสเตอร์ (Clustering Virtualization) การจัดระบบแบบคลัสเตอร์ (Cluster) คือการรวมกลุ่มคอมพิวเตอร์หลายเครื่องให้ทำงานร่วมกันเป็นหนึ่งหน่วย โดยแต่ละเครื่องในคลัสเตอร์เรียกว่า “โหนด (Node)” จุดประสงค์หลักคือเพื่อสร้างระบบที่มีความทนทานต่อความล้มเหลว (Fault Tolerance) และเพิ่มประสิทธิภาพ (Performance) โดยกระจายภาระงาน (Workload) ให้แต่ละโหนดในคลัสเตอร์รับผิดชอบร่วมกัน", 
"page":"122", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2730000c326a949c/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"27. Clustering Virtualization_หน้า115.png", 
"pic_number":"27"},


{"text": "ประเภทของระบบจัดเก็บข้อมูล (Types of Storage) เซิร์ฟเวอร์ทั้งที่อยู่ภายในองค์กรและในระบบคลาวด์สามารถใช้งานโครงสร้างพื้นฐานด้านการจัดเก็บข้อมูลได้หลากหลายรูปแบบ ไม่ว่าจะเป็นในลักษณะของเครื่องจริงหรือเครื่องเสมือน ทั้งในแบบเดี่ยว (Stand-alone) หรือคลัสเตอร์ (Cluster) แม้ว่าเครื่องคอมพิวเตอร์จำนวนมากจะใช้ไดรฟ์ภายใน แต่การจัดเก็บข้อมูลผ่านเครือข่ายก็เป็นอีกทางเลือกหนึ่งที่ตอบโจทย์ประสิทธิภาพที่สูงกว่า บทเรียนนี้จะอธิบายรูปแบบของการจัดเก็บข้อมูล ได้แก่ การจัดเก็บในเครื่อง, การจัดเก็บผ่านอุปกรณ์ NAS และเครือข่าย SAN", 
"page":"126", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac273500041fb5c56b/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"28.Types of Storage_หน้า119.png", 
"pic_number":"28"},


{"text": "การใช้คอนเทนเนอร์แบบสแตนด์อโลน (Stand-Alone Containerization) คอนเทนเนอร์เป็นรูปแบบของการจำลองเสมือน (Virtualization) ที่แตกต่างจากเครื่องเสมือน (Virtual Machine – VM) โดยคอนเทนเนอร์จะเป็นชุดซอฟต์แวร์แบบสมบูรณ์และสามารถพกพาได้ ซึ่งรวมถึงโค้ดของแอปพลิเคชัน รันไทม์ ไลบรารี การตั้งค่าต่าง ๆ และองค์ประกอบอื่น ๆ ที่จำเป็นต่อการทำงานของซอฟต์แวร์ทั้งหมดไว้ในแพ็กเกจเดียว คอนเทนเนอร์สามารถนำไปใช้งานบนแพลตฟอร์มใดก็ได้ที่มีเอนจินของคอนเทนเนอร์ (Container Engine) รวมถึงโครงสร้างพื้นฐานของคลาวด์", 
"page":"129", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2738002833a6f012/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"29.Stand-Alone Containerization_หน้า122.png", 
"pic_number":"29"},


{"text": "ประเภทของพื้นที่จัดเก็บข้อมูล (Storage Types) การจัดเก็บข้อมูลของคอนเทนเนอร์อาจมีความซับซ้อน คอนเทนเนอร์โดยพื้นฐานจะใช้พื้นที่จัดเก็บข้อมูลแบบชั่วคราว (Ephemeral Storage) ซึ่งจะหายไปเมื่อคอนเทนเนอร์ถูกลบหรือล้มเหลว อย่างไรก็ตาม แอปพลิเคชันบางประเภทจำเป็นต้องเก็บข้อมูลไว้นอกช่วงชีวิตของคอนเทนเนอร์ จึงมีการใช้งานพื้นที่จัดเก็บข้อมูล 2 แบบ", 
"page":"134", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac273c002d0dae6edd/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"30.Storage Types_หน้า127.png", 
"pic_number":"30"},


{"text": " แผนภาพการไหลของเครือข่าย (Network Flow Diagram) แผนภาพการไหลของเครือข่ายเป็นเครื่องมือที่ช่วยให้ผู้ใช้งานสามารถมองเห็นและเข้าใจได้ว่า ข้อมูลมีการเคลื่อนผ่านโครงสร้างพื้นฐานของระบบเครือข่ายอย่างไร โดยครอบคลุมถึงโหนดทั้งภายในและภายนอก อุปกรณ์เครือข่าย (เช่น เราเตอร์) ตลอดจนบริการบนคลาวด์ต่าง ๆ", 
"page":"144", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2740001aeef2397e/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"31. Network Flow Diagram_หน้า137.png", 
"pic_number":"31"},


{"text": "VPN แบบไซต์ต่อไซต์ (Site-to-Site VPN) เป็นการเชื่อมต่อแบบ tunneled ระหว่างสองไซต์ที่เป็นระบบเครือข่ายขนาดใหญ่ เช่น สำนักงานหรือศูนย์ข้อมูล ตัวอย่างของการเชื่อมต่อแบบไซต์ต่อไซต์ ได้แก่: จากสำนักงานใหญ่ไปยังสำนักงานสาขา (ใช้ในเครือข่ายอินทราเน็ต), จากศูนย์ข้อมูลเอกชนหนึ่งไปยังอีกแห่งหนึ่ง (ในระบบคลาวด์ส่วนตัว), จากศูนย์ข้อมูลเอกชนไปยังผู้ให้บริการระบบคลาวด์สาธารณะหนึ่งรายหรือมากกว่า (ใช้ในระบบคลาวด์แบบไฮบริด)", 
"page":"147", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac274400053e2a987e/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"32.Site-to-Site VPN_หน้า140.png", 
"pic_number":"32"},


{"text": "VPN แบบจุดต่อไซต์ (Point-to-Site VPN) หรือบางครั้งเรียกว่า VPN แบบเข้าถึงจากระยะไกล (Remote Access VPN) เป็นการเชื่อมต่อระหว่างอุปกรณ์เดี่ยว (เช่น คอมพิวเตอร์ของผู้ใช้งาน) ไปยังเครือข่ายขององค์กรหรือระบบคลาวด์ ในบางบริบท อาจเรียกว่า VPN แบบจุดต่อจุด (Point-to-Point VPN) เนื่องจากเป็นการเชื่อมต่อระหว่างอุปกรณ์เครือข่ายเพียงสองจุด ตัวอย่างของ VPN แบบจุดต่อไซต์: เวิร์กสเตชันที่บ้านเชื่อมต่อกับศูนย์ข้อมูลขององค์กร (ใช้งานจากระยะไกล), เวิร์กสเตชันที่บ้านเชื่อมต่อกับบริการคลาวด์สาธารณะ (เข้าถึงคลาวด์จากระยะไกล), แล็ปท็อปที่ใช้งานระหว่างเดินทางเชื่อมต่อกับศูนย์ข้อมูลหรือผู้ให้บริการคลาวด์", 
"page":"148", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac27470036443f3a6f/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"33.Point-to-Site VPN_หน้า141.png", 
"pic_number":"33"},


{"text": "การรักษาความมั่นคงปลอดภัยด้วย IPsec (IPsec Security) ในการเข้ารหัสข้อมูลของระบบเครือข่ายแบบดั้งเดิม การเข้ารหัสมักดำเนินการในชั้นแอปพลิเคชัน (Application Layer) ซึ่งหมายความว่า ทั้งฝั่งไคลเอนต์และแอปพลิเคชันของระบบเครือข่ายที่ปลายทั้งสองฝั่งของการเชื่อมต่อจะต้องรองรับการเข้ารหัสในรูปแบบเดียวกัน ซึ่งอาจสร้างข้อจำกัดด้านความเข้ากันได้ระหว่างแอปพลิเคชัน", 
"page":"150", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac274b001c10be0dfd/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"34.IPsec Security_หน้าที่143.png", 
"pic_number":"34"},


{"text": "ไฟร์วอลล์สำหรับเว็บแอปพลิเคชัน (Web Application Firewalls – WAF) WAF ทำงานที่ระดับ เลเยอร์ 7 (Application Layer) เพื่อป้องกันช่องโหว่ที่เกิดขึ้นในระดับแอปพลิเคชัน เช่น: Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), SQL Injection, Distributed Denial of Service (DDoS)", 
"page":"155", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac274f00235b6e3f63/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"35.Web Application Firewalls (WAFs)_หน้า148.png", 
"pic_number":"35"},


{"text": "เครือข่ายเดียวที่มีหลายซับเน็ต (Single Virtual Network with Subnets) ในรูปแบบพื้นฐานนี้ ผู้ดูแลระบบคลาวด์จะจัดการเครือข่ายเสมือนเดียวที่ประกอบด้วยหนึ่งหรือหลายซับเน็ต โดยแต่ละซับเน็ตจะมีการจำกัดการรับส่งข้อมูลเฉพาะภายในซับเน็ตนั้น เว้นแต่จะมีการตั้งค่าพิเศษเพิ่มเติม เช่น แบ่งเป็นแผนก “การเงิน” และ “วิศวกรรม” แยกกันในเครือข่ายเดียวกัน", 
"page":"158", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2754000bbad74551/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"36.Single Network with Subnets_หน้า151.png", 
"pic_number":"36"},


{"text": "เครือข่ายเสมือนหลายเครือข่ายแบบเพียร์ (Multiple Virtual Networks Configured as Peers) ในสถานการณ์ที่ซับซ้อนมากขึ้น (และพบได้จริงบ่อย) จะมีเครือข่ายเสมือนหลายเครือข่ายเชื่อมต่อกันแบบเพียร์ (peer-to-peer) และสามารถสื่อสารกันได้อย่างโปร่งใส แต่ละเครือข่ายเสมือนมีซับเน็ตของตนเอง และสามารถอยู่ในเขตภูมิภาค (Region) ของ Azure ที่แตกต่างกันได้", 
"page":"159", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2757000c65af1a06/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"37.Multiple Virtual Networks Configured as Peers_หน้า152.png", 
"pic_number":"37"},


{"text": "เครือข่ายเสมือนแบบศูนย์กลาง-รัศมี (Multiple Virtual Networks in a Hub-and-Spoke Topology) ในกรณีนี้ มีเครือข่ายเสมือนหลายชุดในแต่ละ Region ของ Azure และเครือข่ายภายในแต่ละ Region จะเชื่อมต่อกันผ่านเครือข่ายศูนย์กลาง (Hub VNET) พร้อมกับมีการตั้งค่าให้ Hub ของแต่ละ Region เชื่อมต่อกันเองด้วย ซึ่งช่วยให้สามารถขยายระบบเครือข่ายในแต่ละภูมิภาค และรองรับการสื่อสารข้ามภูมิภาคได้อย่างมีประสิทธิภาพ", 
"page":"160", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac275b00181c2ea94c/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"38. Multiple Virtual Networks in a Hub-and-Spoke Topology_หน้า153.png", 
"pic_number":"38"},


{"text": "ไมโครเซ็กเมนเทชัน (Microsegmentation) การแบ่งเครือข่าย (Segmentation) จะทำในระดับเครือข่ายโดยแยกเซ็กเมนท์ออกจากกัน และป้องกันการเข้าถึงจากภายนอกที่ไม่ได้รับอนุญาต ซึ่งมักใช้ตัวระบุ เช่น IP Address หรือหมายเลขพอร์ต (Port Number) การแบ่งเครือข่ายในระดับเครือข่าย (Network-level segmentation) มักใช้เพื่อแยกการรับส่งข้อมูลที่ขอบเครือข่ายหรือระหว่างลิงก์เฉพาะ (เช่น เราเตอร์) อย่างไรก็ตาม วิธีนี้ไม่สามารถควบคุมความปลอดภัยภายในแต่ละเซ็กเมนท์ได้โดยละเอียด ซึ่งอาจเป็นปัญหาโดยเฉพาะเมื่อแอปพลิเคชันหนึ่งมีบางส่วนทำงานในระบบภายใน (On-premises) และบางส่วนในคลาวด์", 
"page":"161", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac2761001342675143/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"39.Microsegmentation_หน้า154.png", 
"pic_number":"39"},


{"text": "เทคโนโลยีเครือข่ายแลนเสมือน (Virtual LAN Technologies) การแบ่งเครือข่ายแบบพื้นฐานใช้เราเตอร์ชั้นที่ 3 (Layer 3) เพื่อเชื่อมต่อกับซับเน็ต IP ที่แยกจากกัน โหนดในเครือข่ายจะเชื่อมต่อกับสวิตช์ และสามารถสื่อสารกับโหนดอื่น ๆ ที่เชื่อมต่อกับสวิตช์เดียวกัน สวิตช์จะเชื่อมต่อกับเราเตอร์ ซึ่งทำหน้าที่เป็นขอบเขตของซับเน็ต โดยเราเตอร์จะเชื่อมต่อหลายซับเน็ต และมีการตั้งกฎเพื่อจัดการการสื่อสารระหว่างซับเน็ตเหล่านั้น", 
"page":"165", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac276500117a0aaf38/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"40.Virtual LAN Technologies_หน้า158.png", 
"pic_number":"40"},


{"text": "เครือข่ายที่กำหนดโดยซอฟต์แวร์ (Software-Defined Networking - SDN) เครือข่ายแบบดั้งเดิมมีการกระจายตัว ผู้ดูแลระบบต้องกำหนดค่าแต่ละสวิตช์หรือเราเตอร์แยกกัน การอัปเดตหรือสำรองข้อมูลทำได้ยาก", 
"page":"167", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac276900326a20d141/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"41.Software-Defined Networking_หน้า160.png", 
"pic_number":"41"},


{"text": "เครือข่ายส่งเนื้อหา (Content Delivery Networks – CDNs) เครือข่ายส่งเนื้อหา หรือ CDN เป็นโครงสร้างเครือข่ายแบบกระจาย (Distributed Network) ที่มีมาตั้งแต่ช่วงทศวรรษ 1990 โดยมีวัตถุประสงค์เพื่อเพิ่มความพร้อมใช้งาน (Availability) และประสิทธิภาพ (Performance) โดยใช้การแคช (Cache) เนื้อหาหรือบริการให้อยู่ใกล้กับผู้ใช้งานมากที่สุด", 
"page":"171", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac276d0034cf983ce5/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"42.Content Delivery Network_หน้า164.png", 
"pic_number":"42"},


{"text": "ทรัพยากรการประมวลผลสำหรับคอนเทนเนอร์ (Compute Resources for Containers) ผู้ให้บริการระบบคลาวด์ (Cloud Service Providers: CSPs) หลายแห่งได้พัฒนาอินสแตนซ์ที่ออกแบบมาโดยเฉพาะสำหรับการใช้งานคอนเทนเนอร์ ซึ่งอินสแตนซ์เหล่านี้สามารถจัดสรรทรัพยากรหน่วยประมวลผลกลาง (CPU) และหน่วยความจำ (Memory) ให้เหมาะสมกับลักษณะของงานได้ ทั้งยังสามารถ “จัดสรรเกินความต้องการ” (Over-allocate) ได้ในบางกรณี เพื่อรองรับภาระงานที่ผันผวน", 
"page":"173", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac27760024a7ef9ca0/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"43. Dynamic Host Configuration Protocol_หน้า166.png", 
"pic_number":"43"},


{"text": "ทรัพยากรการประมวลผลสำหรับคอนเทนเนอร์ (Compute Resources for Containers) ผู้ให้บริการระบบคลาวด์ (Cloud Service Providers: CSPs) หลายแห่งได้พัฒนาอินสแตนซ์ที่ออกแบบมาโดยเฉพาะสำหรับการใช้งานคอนเทนเนอร์ ซึ่งอินสแตนซ์เหล่านี้สามารถจัดสรรทรัพยากรหน่วยประมวลผลกลาง (CPU) และหน่วยความจำ (Memory) ให้เหมาะสมกับลักษณะของงานได้ ทั้งยังสามารถ “จัดสรรเกินความต้องการ” (Over-allocate) ได้ในบางกรณี เพื่อรองรับภาระงานที่ผันผวน", 
"page":"254", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac277b0000f534bd75/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"44.Compute Resources for Containers_หน้า247.png", 
"pic_number":"44"},


{"text": "การวิเคราะห์ไฟล์ล็อก (Log File Analysis) การวิเคราะห์ล็อก คือกระบวนการทำความเข้าใจและตอบสนองต่อเหตุการณ์ที่ถูกบันทึกไว้ในไฟล์ล็อก โดยแต่ละรายการจะระบุระดับความรุนแรง (severity) รายละเอียดของระบบที่ได้รับผลกระทบ ผู้ใช้ที่เกี่ยวข้อง (ถ้ามี) รวมถึงสาเหตุของเหตุการณ์นั้น ๆทั้งระบบ rsyslog ของ Linux และ Event Viewer ของ Windows มีการจำแนกระดับความรุนแรงของเหตุการณ์ เช่น:EMERG (0): ระบบไม่สามารถใช้งานได้ ALERT (1): จำเป็นต้องดำเนินการทันที CRIT (2): สภาวะวิกฤต ERR (3): สภาวะผิดพลาด WARNING (4): สภาวะแจ้งเตือน NOTICE (5): เหตุการณ์สำคัญแต่ไม่ใช่ปัญหา INFO (6): ข้อมูลทั่วไป DEBUG (7): ข้อความระดับการดีบัก", 
"page":"263", 
"path":"https://sgp.cloud.appwrite.io/v1/storage/buckets/69ac25ec00381b4093cd/files/69ac277e001645ed2f24/view?project=69ac25db001ba9924db7&mode=admin", 
"pic_name":"45. Log File Analysis_หน้า256.png", 
"pic_number":"45"}

]

# --- 3. ดึงเฉพาะ text ออกมาทำ Vector พร้อมกันทั้งหมด ---
print(f"กำลังแปลงข้อมูลเป็น Vector จำนวน {len(data_to_insert)} รายการ (Batch Processing)...")
texts = [item['text'] for item in data_to_insert]
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True).tolist()

# --- 4. นำ Vector กลับไปใส่ใน Dictionary แต่ละตัว ---
for i, item in enumerate(data_to_insert):
    item['embedding'] = embeddings[i]

# --- 5. บันทึกลง MongoDB ทีเดียวทั้งหมด ---
print("กำลังนำข้อมูลและ Vector ขึ้น MongoDB...")
collection.insert_many(data_to_insert)

print(f"🎉 สำเร็จ! บันทึกข้อมูลเข้า Database ทั้งหมด {len(data_to_insert)} รายการเรียบร้อยแล้วครับ")