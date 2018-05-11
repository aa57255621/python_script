# -*- coding: utf-8 -*-
'''
1. 每天周五下午19点自动弹出提示框，提醒我发周报(自动提醒的功能，windows用任务计划程序，linux用crontab)
   如果用python实现普通的定时，比如睡眠多久执行，但是每天周五下午19点这个定时比较特殊，但是python里也有方法实现
   我使用过定时任务框架APScheduler，就可以实现这个功能，但是针对现在的这个问题，由于使用APScheduler在子线程中更新了UI，所以导致
   UI界面未响应，所以我舍弃了这个框架，改用系统的方法，但是不涉及UI的可以用该框架，或许UI也可以用，但是我没有找到好的方法
2. 在代码里填上你的邮箱，密码，服务器即可
2. 填写提示框里的内容，点击发送邮件即可
'''
import sys
import yagmail
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QInputDialog, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import QCoreApplication, Qt, QThread
from PyQt5.QtGui import QFont
import time

#提醒框
class AlertWeekly(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		# 从(600, 300)位置开始，显示一个300*100的界面
		self.setGeometry(600, 300, 300, 100)
		self.setWindowTitle('写周报')
		#设置窗口总是在最前面
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.label = QLabel('兄弟，该写周报了！', self)
		self.label.move(30, 20)
		self.label.setFont(QFont('楷体', 20, QFont.Bold))

		self.btnCertain = QPushButton('好的', self)
		self.btnCertain.move(60, 60)
		
		self.btnCancel = QPushButton('不写', self)
		self.btnCancel.move(170, 60)
		self.btnCancel.clicked.connect(self.closeDialog)

	def closeDialog(self):
		self.close()

# 发送邮件界面
class WriteWeekly(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setGeometry(400, 100, 600, 500)
		self.setWindowTitle('发送邮件')

		#需要使用嵌套布局，整体是垂直布局(网格布局+水平布局)，水平布局放两个按钮
		self.wwg = QWidget(self)
		self.wlayout = QVBoxLayout(self.wwg)
		self.creatGridLayout()
		self.createHLayout()

		self.wlayout.addLayout(self.grid)
		self.wlayout.addLayout(self.hlayout)

		self.setLayout(self.wlayout)

	def creatGridLayout(self):
		self.grid = QGridLayout()
		self.receiverLabel = QLabel('收件人：', self)
		self.receiverEdit = QLineEdit(self)
		self.subjectLabel = QLabel('主题：', self)
		self.subjectEdit = QLineEdit(self)
		self.fileLabel = QLabel('附件：', self)
		self.fileBtn = QPushButton('选择文件', self)
		self.fileBtn.clicked.connect(self.selectFile)
		self.contentLabel = QLabel('内容：', self)
		self.contentEdit = QTextEdit(self)
		self.receiverEdit.setFont(QFont('Microsoft YaHei UI', 11))
		self.subjectEdit.setFont(QFont('Microsoft YaHei UI', 11))
		self.contentEdit.setFont(QFont('Microsoft YaHei UI', 11))
		#设置网格间的距离
		self.grid.setSpacing(10)
		self.grid.addWidget(self.receiverLabel, 1, 0)
		self.grid.addWidget(self.receiverEdit, 1, 1)
		self.grid.addWidget(self.subjectLabel, 2, 0)
		self.grid.addWidget(self.subjectEdit, 2, 1)
		self.grid.addWidget(self.fileLabel, 3, 0)
		self.grid.addWidget(self.fileBtn, 3, 1)
		self.grid.addWidget(self.contentLabel, 4, 0)
		self.grid.addWidget(self.contentEdit, 4, 1, 20,1)

	def createHLayout(self):
		self.hlayout = QHBoxLayout()
		self.sendBtn = QPushButton('发送', self)
		self.cancelBtn = QPushButton('取消', self)
		self.cancelBtn.clicked.connect(self.close)

		self.hlayout.addStretch(3)
		self.hlayout.addWidget(self.sendBtn)
		self.hlayout.addStretch(1)
		self.hlayout.addWidget(self.cancelBtn)
		self.hlayout.addStretch(3)

	def selectFile(self):
		self.filename, _ = QFileDialog.getOpenFileName(self)
		self.fileBtn.setText(self.filename)

	def showDialog(self):
		self.show()
	
	# 关闭窗口时提醒
	def closeEvent(self, event):
		reply = QMessageBox.question(self, '确认', '确认退出吗', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			event.accept()        
		else:
			event.ignore()

	def sendEmail(self):
		# 登录邮箱
		yag = yagmail.SMTP(user = 'xxxx@xxx.com', password = 'xxxx', host = 'xxxx.com', port = '', smtp_starttls = False)
		# 收件人,允许多个收件人，用;隔开
		to = self.receiverEdit.text().split(';')
		# 主题
		subject = self.subjectEdit.text()
		# 附件
		files = self.fileBtn.text()
		if files == '选择文件':
			files = ''
		# 内容
		contents = self.contentEdit.toPlainText()
		# 发送(to:收件人，subject：邮箱主题，contents: 邮箱内容,附件：contents = [contents, 'C://Users//Desktop//log.txt'])
		yag.send(to = to, subject = subject, contents = [contents, files])
		print('%s\n %s\n %s\n %s\n' % (to, subject, files, contents))
		# 发送成功后清空文本内容
		QMessageBox.about(self, '结果', '发送成功')
		self.receiverEdit.clear()
		self.subjectEdit.clear()
		self.contentEdit.clear()
		self.fileBtn.setText('选择文件')

if __name__ == '__main__':
	app = QApplication(sys.argv)
	alertDialog = AlertWeekly()
	writeDialog = WriteWeekly()
	# 确认按钮按下，先关闭提醒窗口，再打开写邮件的窗口
	alertDialog.btnCertain.clicked.connect(alertDialog.closeDialog)
	alertDialog.btnCertain.clicked.connect(writeDialog.showDialog)
	# 发送邮件
	writeDialog.sendBtn.clicked.connect(writeDialog.sendEmail)
	alertDialog.show()
	sys.exit(app.exec_()) 
