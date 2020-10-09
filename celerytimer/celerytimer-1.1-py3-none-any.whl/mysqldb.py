import datetime

import pymysql


class TimingTask(object):

    def __init__(self, host, port, user, password, database):
        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database,
                                    charset='utf8')
        self.cursor = self.conn.cursor()
        self.table_name = "celery_timer"
        self.create_db()

    @staticmethod
    def construct_key(task: str, timestamp: str, flag: str, unique: list) -> str:
        """组合key
        Keyword Arguments:
            ----
            task: 任务名称
            timestamp: 时间戳
            flag: 任务标识
            unique: 数据库唯一索引
        return key列表
        """
        key = f"{task}_{flag}_{timestamp}__{':'.join(unique)}"
        return key

    @staticmethod
    def get_key_list(task: str, flag: str, data: dict, sql_unique: list) -> list:
        """批量组合key
        Keyword Arguments:
            ----
            task: 任务名称
            flag: 任务标识
            data: 任务数据 {时间戳:[{},{},{},...]}
            sql_unique: 数据库唯一索引，从executed_data中获取该字段的值
        return key列表
        """
        key_list = []
        for timestamp, tmp_data in data.items():
            for _data in tmp_data:
                unique = [str(_data.get(key)) for key in sql_unique]
                key = TimingTask.construct_key(task, timestamp, flag, unique)
                key_list.append(key)
        return key_list

    def create_db(self):
        """
        id 索引
        task_name    任务昵称
        task    任务名
        flag    唯一标识
        key     唯一的key值
        status  任务状态（0未执行，1执行成功，2执行失败）
        executed_time   任务的执行时间
        finish_time     任务完成时间
        update_time     更新时间
        create_time     创建时间
        """
        CREATE_SQL = """
            CREATE TABLE IF NOT EXISTS `%s`(
            `id` int NOT NULL AUTO_INCREMENT,   
            `task_name` varchar(255) DEFAULT NULL,
            `task` varchar(255) DEFAULT NULL,
            `flag` varchar(255) DEFAULT NULL,
            `key` varchar(255) DEFAULT NULL,
            `status` int DEFAULT NULL,
            `executed_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
            `finish_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
            `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
            `create_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            UNIQUE KEY `key_UNIQUE` (`key`)
            ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4
        """ % (self.table_name,)
        self.cursor.execute(CREATE_SQL)

    def filter_and_save_task(self, task: str, task_name: str, flag: str, executed_data: dict, sql_unique: list,
                             repeatable: bool):
        """数据检查校验
        Keyword Arguments:
            ----
            task: 任务名称
            task_name: 任务昵称
            flag: 任务标识
            executed_data: 执行任务的数据：{时间戳:[{},{},...],...}
            sql_unique: 任务数据的唯一索引
            repeatable: 是否可以重复该任务 False不允许/True允许
        return: 返回没有被记录的数据 {时间戳:[{},{},...]}
        """
        filter_data_dict, values_list = dict(), list()
        SAVE_SQL = """INSERT INTO `%s`""" % self.table_name + """
                        (task,task_name,flag,executed_time,`key`) values (%s,%s,%s,%s,%s)
                       """
        for timestamp, task_data_list in executed_data.items():
            new_key_list = self.get_key_list(task, flag, {timestamp: task_data_list}, sql_unique)
            FIND_SQL = """
                SELECT `key` 
                FROM `%s`""" % self.table_name + """
                WHERE `key` in %s
                """
            self.cursor.execute(FIND_SQL, (new_key_list,))
            old_datas = self.cursor.fetchall()
            old_key_list = list()
            for old_data in old_datas:
                old_key_list.append(old_data[0])

            for index, unique_data in enumerate(new_key_list):
                if unique_data in old_key_list:
                    continue
                executed_time = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                values_list.append((task, task_name, flag, executed_time, unique_data))

                # 把旧的任务过滤掉，只返回新的任务
                if filter_data_dict.get(timestamp):
                    filter_data_dict[timestamp].append(task_data_list[index])
                else:
                    filter_data_dict[timestamp] = [task_data_list[index]]
        try:
            self.cursor.executemany(SAVE_SQL, values_list)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

        if repeatable:
            return executed_data
        else:
            return filter_data_dict

    def update_task_status(self, task: str, flag: str, executed_data: dict, sql_unique: list, status: int):
        """更新任务状态
        Keyword Arguments:
            ----
            task: 任务名称
            flag: 任务标识
            executed_data: 执行任务的数据：{时间戳:[{},{},...],...}
            sql_unique: 任务数据的唯一索引
            status: 任务状态
        return:
        """
        key_lists = list()
        for timestamp, task_data_list in executed_data.items():
            key_list = self.get_key_list(task, flag, {timestamp: task_data_list}, sql_unique)
            key_lists.extend(key_list)
        now = datetime.datetime.now()
        UPDATE_SQL = """
            UPDATE `%s`""" % self.table_name + """ 
            SET status=%s,finish_time=%s
            WHERE `key` in %s
        """
        try:
            self.cursor.execute(UPDATE_SQL, (status, now, key_lists))
            self.conn.commit()
        except Exception as e:
            # 发生错误时回滚
            self.conn.rollback()
            raise e
