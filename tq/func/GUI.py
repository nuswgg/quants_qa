## https://zhuanlan.zhihu.com/p/351117835

import sys
from PyQt5.QtWidgets import *  # 各物件都在QtWidgets模块中，所以一次全导入
from tqsdk import TqApi, TqAccount, TqAuth, TqKq

class DengLu(QWidget):  # 定义窗口类，继承于QWidget
    def __init__(self):
        super().__init__()  # 调用父类QWidget初始化方法
        self.resize(500, 300)  # 设置窗口大小,长和高
        self.setWindowTitle('账户登陆')  # 设置窗口标题
        self.xinyiid = QLabel("信易账号")  # 创建标签，并传入标签内容，也可无参数
        # self.xinyiid.setText("信易账号") #无参数时，标签内容也可用setText方法设置
        # self.xinyimima = QLabel("信易密码")
        # self.brokerid = QLabel("期货公司")
        # self.usernumber = QLabel("期货账号")
        # self.password = QLabel("交易密码")
        self.Getin = QPushButton("登录")  # 创建按钮，并传入按钮名称，也可无参数
        # self.Getin.setText("登录") #无参数时，按钮名称也可用setText方法设置
        self.Getout = QPushButton("退出")
        self.BrokerId = QComboBox()  # 创建下拉列表框
        self.BrokerId.addItem("快期模拟")  # 按顺序添加下拉选项
        self.BrokerId.addItem("simnow")
        self.BrokerId.addItem("H期货公司")
        self.Xinyiid = QLineEdit()  # 创建输入框，用来输入信易账号
        self.Xinyimima = QLineEdit()  # 用来输入信易密码
        self.Usernumber = QLineEdit()  # 用来输入期货账号
        self.Password = QLineEdit()  # 用来输入期货交易密码
        self.textBrowser = QTextBrowser()  # 创建文本框，用setText方法设置需要显示的文本
        self.textBrowser.setText('免责声明\n本软件是基于天勤量化（TqSdk）开发的UI界面，由于软件开发本身的复杂性，\
无法保证软件完全没有错误，您选择使用本软件即表示您同意错误和/或遗漏的存在，在任何情况下本软件及其开发者对于直接、\
间接、特殊的、偶然的、或间接产生的、使用或无法使用本软件进行交易和投资造成的盈亏、直接或间接引起的赔偿、损失、债务或\
是任何交易中止均不承担责任和义务。\n此声明永久有效。\n本软件应配合其他交易软件一块使用。\n推荐您通过天勤量化（TqSdk）平台开发符合自己交易需求的UI软件。')

        self.formlayout = QFormLayout()  # 创建表单布局
        self.formlayout.addRow(self.xinyiid, self.Xinyiid)  # 添加一行，标签和输入框对应
        self.formlayout.addRow("信易密码", self.Xinyimima)  # 直接输入字符串也会自动创建为标签
        self.formlayout.addRow("期货公司", self.BrokerId)
        self.formlayout.addRow("期货账号", self.Usernumber)
        self.formlayout.addRow("交易密码", self.Password)
        self.formlayout.setVerticalSpacing(10)  # 设置行距

        self.horizontalLayout1 = QHBoxLayout()  # 创建水平布局1
        self.horizontalLayout1.addWidget(self.Getin)  # 按顺序把按钮添加到水平布局中
        self.horizontalLayout1.addWidget(self.Getout)

        self.verticalLayout = QVBoxLayout()  # 创建垂直布局
        self.verticalLayout.addLayout(self.formlayout)  # 按顺序把表单布局和水平布局1添加到垂直布局中
        self.verticalLayout.addLayout(self.horizontalLayout1)
        self.verticalLayout.setContentsMargins(0, 10, 0, 40)  # 设置部件与窗口边缘的距离，(左,上,右,下)

        self.horizontalLayout2 = QHBoxLayout()  # 创建水平布局2
        self.horizontalLayout2.addLayout(self.verticalLayout)  # 按顺序把垂直布局和文本框添加到水平布局2中
        self.horizontalLayout2.addWidget(self.textBrowser)

        self.setLayout(self.horizontalLayout2)  # 把水平布局2设置为窗口的最终布局

        self.Getout.clicked.connect(self.close)  # 建立信号槽，点击退出按钮连接到函数close()
        self.Getin.clicked.connect(self.getin)  # 点击登录按钮连接到函数getin()

    def getin(self):  # 用来登录账户
        global api  # 声明api为全局变量，便于在其他函数中使用
        XinyiId = self.Xinyiid.text()  # 获取输入框里的内容，信易账号
        XinyiMima = self.Xinyimima.text()  # 信易密码
        BrID = self.BrokerId.currentText()  # 获取下拉框当前的选项
        Usname = self.Usernumber.text()  # 期货账号
        Psword = self.Password.text()  # 期货交易密码
        try:
            if BrID == '快期模拟':
                api = TqApi(TqKq(), auth=TqAuth(XinyiId, XinyiMima))
            else:
                api = TqApi(TqAccount(BrID, Usname, Psword), auth=TqAuth(XinyiId, XinyiMima))
            account = api.get_account()
            print("登陆成功，可用资金: %.2f" % (account.available))
            self.close()  # 登录成功关闭窗口
        except Exception:  # 登录失败，弹出警告窗口
            QMessageBox.warning(self, '登录错误', '登录失败，请检查输入重新登录', QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Deng_Lu = DengLu()  # 实例化窗口
    Deng_Lu.show()  # 显示窗口
    sys.exit(app.exec_())