from ftplib import FTP

class myFtp(FTP):
    encoding='UTF-8'
    def getSubdir(self, *args):
        '''拷贝了 nlst() 和 dir() 代码修改，返回详细信息而不打印'''
        cmd = 'LIST'
        func = None
        if args[-1:] and type(args[-1]) != type(''):
            args, func = args[:-1], args[-1]
        for arg in args:
            cmd = cmd + (' ' + arg)
        files = []
        self.retrlines(cmd, files.append)
        return files

    def getdirinfo(self, dirname=None):
        """返回目录列表，包括文件简要信息"""
        if dirname != None:
            self.cwd(dirname)
        lst = self.getSubdir()
        print(lst)
        # 处理返回结果，只需要目录名称
        newlst = []
        for line in lst:
            string = ''
            i = 0
            for letter in line:
                if letter != ' ':
                    if i in [1,3,5,7,9,11,13]:
                        i = i + 1
                    string = string + letter
                else:
                    if i in [1,3,5,7,9,11,13]:
                        continue
                    i = i + 1
                    string = string + letter
                    if i in [1,3,5,7,9,11,13]:
                        continue
            newlst.append(string)
        print(newlst)
        fileinfo = []
        for i in newlst:
            string = ' '
            tempinfo = []
            tempi = i.split(' ')
            tempinfo.append(string.join(tempi[8:]))
            if tempi[0][0] == 'd':
                tempinfo.append('Folder')
                tempinfo.append('')
            else:
                tempinfo.append('File')
                tempinfo.append(tempi[4])
            tempinfo.append(tempi[0])
            tempinfo.append(tempi[5] + ' ' + tempi[6] + ' ' + tempi[7])
            fileinfo.append(tempinfo)
        return fileinfo

    def getfiles(self, dirname=None):
        """返回文件列表，简要信息"""
        if dirname != None:
            self.cwd(dirname)  # 设置FTP当前操作的路径
        return self.nlst()  # 获取目录下的文件