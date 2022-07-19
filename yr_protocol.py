from struct import *

"""
协议版本 0x10
2022-7-17
"""


class YRDecoder:
    def __init__(self):
        self.msg_type_dict = {
            0x10: self.__decode_control, 'control': self.__encode_control,
            0x14: self.__decode_route_plan, 'track/planning': self.__encode_route_plan,
            0x18: self.__decode_payload, 'mission/planning/cb': self.__encode_payload,
            0x1c: self.__decode_link, 'link/planning/cb': self.__encode_link,
            0x20: self.__decode_pic, 'image/cb': self.__encode_pic,
            0x24: self.__decode_video, 'video/cb': self.__encode_video,
            0x28: self.__decode_track, 'track/cb': self.__encode_track,
            0x2c: self.__decode_remote_control, 'control/cb': self.__encode_remote_control,
            0x30: self.__decode_remote_measurement, 'telemetry/cb': self.__encode_remote_mesurement,
            0x34: self.__decode_return, 'return/cb': self.__encode_return,
        }

    # 控制指令
    def __decode_control(self, ctx, _res):
        ctx = unpack("<HHBBBBBBB", ctx)
        _res['control'] = "{:x}".format(ctx[0])
        _res['time'] = "{},{},{},{},{},{},{}".format(ctx[7], ctx[6], ctx[5], ctx[4], ctx[3], ctx[2], ctx[1])
        _res['topic'] += 'control'
        return _res

    def __encode_control(self, ctx):
        time = ctx['time'].split(',')
        _res = pack("<HHBBBBBB", int(ctx['control_cb'], 16),  # 无人平台发送控制开关指令
                    int(time[6]), int(time[5]), int(time[4]), int(time[3]), int(time[2]), int(time[1]), int(time[0]))
        return _res, 0x10

    # 航路规划信息
    def __decode_route_plan(self, ctx, _res):
        # n = ctx[:3]
        # print(n)
        print("编号，规划点数量，生成时间不明确，暂时直接给定")
        seq_id, route_point_n, generate_time = 0, 0x0c, 0
        _res['req'] = str(seq_id)
        _res['num'] = str(route_point_n)
        _res['time'] = str(generate_time)
        airline = []
        i = 3
        for j in range(route_point_n):
            llt = unpack('<BllL', ctx[i:i + 13])
            llt_json = {
                "longitude": round(llt[1] * 180 / 648000000, 7),
                "latitude": round(llt[2] * 90 / 324000000, 7),
                "time": str(llt[3])
            }
            airline.append(llt_json)
            i = i + 13
        _res['airline'] = airline
        _res['topic'] += 'track/planning'
        return _res

    def __encode_route_plan(self, ctx):
        time = ctx['time'].split(',')
        _res = pack("<HBBBBBBBH",
                    int(time[6]), int(time[5]), int(time[4]), int(time[3]), int(time[2]), int(time[1]), int(time[0]),
                    int(ctx['seq']),  # 航路规划编号
                    int(ctx['status'])  # 反馈状态
                    )
        return _res, 0x16

    # 光电载荷信息
    def __decode_payload(self, ctx, _res):
        param_name = ['OperatingCommand', 'OperatingMode', 'OperatingParam', 'OperatingFrequency']
        # c2 由c1 动态解析
        c1, c2, c3 = ctx[:3], ctx[3:len(ctx) - 9], ctx[-9:]
        _res['topic'] += 'mission/planning'
        payload_id, dev_type, param_valid = unpack("<BBB", c1)
        _res['seq'] = str(payload_id)
        _res['category'] = "{:02x}".format(dev_type)

        # # 根据参数为判断是否有数据更新频率字段
        decode_mask = "<" + "B" * len(c2)
        c2_d = unpack(decode_mask, c2)

        i = j = 0
        while param_valid != 0:
            if param_valid & 0x01:
                _res[param_name[i]] = str(c2_d[j])
                j = j + 1
            i = i + 1
            param_valid = param_valid >> 1

        t = unpack("<HBBBBBBB", c3)
        _res['time'] = "{},{},{},{},{},{},{}".format(t[6], t[5], t[4], t[3], t[2], t[1], t[0])
        return _res

    def __encode_payload(self, ctx):
        t = ctx['time'].split(',')
        _res = pack("<HBBBBBBBH",
                    int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[2]), int(t[1]), int(t[0]),
                    int(ctx['seq']),  # 任务载荷编号
                    int(ctx['status'])  # 反馈状态
                    )
        return _res, 0x1a

    # 链路规划信息
    def __decode_link(self, ctx, _res):
        _res['topic'] += 'link/planning'
        ctx = unpack("<BBLHBBBBBBB", ctx)
        _res['seq'] = str(ctx[0])
        _res["command"] = str(ctx[1])
        _res["frequency"] = "{:x}".format(ctx[2])
        _res['time'] = "{},{},{},{},{},{},{}".format(ctx[-2], ctx[-3], ctx[-4], ctx[-5], ctx[-6], ctx[-7], ctx[-8])
        return _res

    def __encode_link(self, ctx):
        t = ctx['time'].split(',')
        _res = pack("<HBBBBBBBH",
                    int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[2]), int(t[1]), int(t[0]),
                    int(ctx['seq']),  # 链路编号
                    int(ctx['status'])  # 反馈状态
                    )
        return _res, 0x1e

    # 图像信息
    def __decode_pic(self, ctx, _res):
        ctx = unpack("<HBBBBBBB", ctx)
        _res['topic'] += 'image/get'
        _res['seq'] = str(ctx[-1])
        _res['time'] = "{},{},{},{},{},{},{}".format(ctx[-2], ctx[-3], ctx[-4], ctx[-5], ctx[-6], ctx[-7], ctx[-8])
        return _res

    def __encode_pic(self, ctx):
        t = ctx['time'].split(',')
        _res = pack("<HBBBBBBLHHL",
                    int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[3]), int(t[1]), int(t[0]),
                    int(ctx['length']),  # 图片文件总长度
                    int(ctx['seq']),  # 图片分块序号
                    int(ctx['num']),  # 图片文件块总长度
                    len(ctx['data'])  # 当前图片长度
                    ) + bytes.fromhex(ctx['data'])  # 图片数据
        return _res, 0x22

    # 视频信息
    def __decode_video(self, ctx, _res):
        ctx = unpack("<HBBBBBBB", ctx)
        _res['topic'] += 'video/get'
        _res['seq'] = str(ctx[-1])
        _res['time'] = "{},{},{},{},{},{},{}".format(ctx[-2], ctx[-3], ctx[-4], ctx[-5], ctx[-6], ctx[-7], ctx[-8])
        return _res

    def __encode_video(self, ctx):
        t = ctx['time'].split(',')
        rtsp = ctx['rtsp'].encode("utf-8")
        _res = pack("<HBBBBBBH",
                    int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[3]), int(t[1]), int(t[0]),
                    len(rtsp)  # rtsp 地址长度
                    ) + rtsp  # rtsp地址
        return _res, 0x26

    # 遥控指令
    def __decode_remote_control(self, ctx, _res):
        ctx = unpack("<BHBBBBBB", ctx)
        _res['topic'] += 'control/get'
        _res['seq'] = str(ctx[0])
        return _res

    def __encode_remote_control(self, ctx):
        t = ctx['time'].split(',')
        _res = pack("<BHHBLBBBLHBBBBBB",
                    int(ctx['seq']),  # 遥控指令编号
                    int(ctx['sail_switch_command']),  # 飞行开关指令
                    int(ctx['sail_control_command']),  # 飞行控制指令
                    int(ctx['link_switch_command']),  # 链路开关指令
                    int(ctx['link_frequency']),  # 通信频率
                    int(ctx['catogary_seq'], 16),  # 载荷类别码
                    int(ctx['mission_device_switch_control']),  # 载荷控制开关
                    int(ctx['mission_device_mode']),  # 载荷工作模式
                    int(ctx['mission_device_param']),  # 载荷工作参数
                    int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[3]), int(t[1]), int(t[0])
                    )
        return _res, 0x2e

    # 航路轨迹信息
    def __decode_track(self, ctx, _res):
        ctx = unpack("<HBBBBBB", ctx)
        _res['topic'] += 'track/get'
        _res['time'] = "{},{},{},{},{},{},{}".format(ctx[0], ctx[1], ctx[2], ctx[3], ctx[4], ctx[5], ctx[6])
        return _res

    def __encode_track(self, ctx):
        t = ctx['time'].split(',')
        airline = ctx['airline']
        _res = pack("<HBBBBBBB",
                    int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[3]), int(t[1]), int(t[0]),
                    len(ctx['airline'])  # 航点数量
                    )
        for i in range(len(airline)):
            sp = pack("<BllL", i,  # 航点序号
                      round(float(airline[i]['longitude']) * 648 * 1e6 / 180),  # 航点经度
                      round(float(airline[i]['latitude']) * 324 * 1e6 / 900),  # 航点纬度
                      int(airline[i]['time'])  # 航点到达时间
                      )
            _res += sp
        return _res, 0x2a

    # 遥测指令
    def __decode_remote_measurement(self, ctx, _res):
        ctx = unpack("<HBBBBBB", ctx)
        _res['topic'] += 'telemetry/get'
        _res['time'] = "{},{},{},{},{},{},{}".format(ctx[0], ctx[1], ctx[2], ctx[3], ctx[4], ctx[5], ctx[6])
        return _res

    def __encode_remote_mesurement(self, ctx):
        t = ctx['time'].split(',')
        _res = pack("<llHHHBBBHBBBBBB",
                    round(float(ctx['longitude']) * 648 * 1e6 / 180),  # 无人平台精度
                    round(float(ctx['latitude']) * 324 * 1e6 / 90),  # 无人平台纬度
                    round(float(ctx['speed'])),  # 平台速度
                    round(float(ctx['altitude'])) + 1000,  # 海拔
                    round(float(ctx['yaw']) * 100),  # 航向
                    int(ctx['mission_device_switch_control'], 16),  # 任务载荷开关状态
                    int(ctx['mission_device_param'], 16),  # 任务载荷开关参数
                    int(ctx['link_status'], 16),  # 通信链路状态
                    int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[3]), int(t[1]), int(t[0])
                    )
        return _res, 0x32

    # 返航信息
    def __decode_return(self, ctx, _res):
        ctx = unpack("<BHBBBBBB", ctx)
        _res['topic'] += 'return'
        _res['seq'] = str(ctx[0])
        _res['time'] = "{},{},{},{},{},{},{}".format(ctx[7], ctx[6], ctx[5], ctx[4], ctx[3], ctx[2], ctx[1])
        return _res

    def __encode_return(self, ctx):
        t = ctx['time'].split(',')
        airline = ctx['airline']
        _res = pack("<BllB",
                    int(ctx['seq']),
                    round(float(ctx['target_longitude']) * 648 * 1e6 / 180),  # 返航精度
                    round(float(ctx['target_latitude']) * 324 * 1e6 / 900),  # 返航纬度
                    len(airline)
                    )

        for i in range(len(airline)):
            sp = pack("<BllL", i,
                      round(float(airline[i]['longitude']) * 648 * 1e6 / 180),  # 路径点经度
                      round(float(airline[i]['latitude']) * 324 * 1e6 / 900),  # 路径点纬度
                      int(airline[i]['time'])  # 路径到达时间
                      )
            _res += sp
        time = pack("<HBBBBBB", int(t[6]), int(t[5]), int(t[4]), int(t[3]), int(t[3]), int(t[1]), int(t[0]))
        _res += time
        return _res, 0x2a

    # 非私有的供调用的函数
    def decode(self, request):
        _res = {"status": 'error'}
        # 消息小于11，必定不完整
        if len(request) < 11:
            return _res
        # 先判断校验和
        cks = request[-1]
        _sum = 0
        for i in range(len(request) - 1):
            _sum += request[i]
        if _sum & 0xff != cks:
            print("校验错误!应该为：{:02x}".format(_sum & 0xff))
            return _res
        # 解析消息头
        h, c = unpack('<BBHBBLBB', request[:12]), request[12:-1]
        # 再判断长度和报文长度是否匹配,即简单判断报文是否正确  不需要了，校验保证了内容的正确 ..仍然需要，对面会瞎发
        if h[2] != len(request):
            print("长度错误!期望：{}实际:{}".format(h[2], len(request)))
            return _res
        # 判断协议版本
        if h[1] != 0x10:
            print("版本号错误!")
            return _res
        # 将报文戳放到json中
        _res['msgId'] = str(h[5])
        # 判断载荷目标
        if h[7] == 0x62:
            _res['topic'] = "/domain/dji/"
        elif h[7] == 0x72:
            _res['topic'] = "/domain/vehicle/"
        else:
            print("无效设备")
            return _res
        # todo: 判断内容长度，是否为总长减头尾，否则报错
        # 根据报文类型解析内容
        _res = self.msg_type_dict[h[4]](c, _res)
        _res['status'] = 'ok'
        return _res

    def encode(self, request):
        try:
            # todo：对内容进行判断，防止没有出错  不需要了 try catch 一键解决
            u01_reverse = {'dji': 0x62, 'vehicle': 0x72}
            k = request['topic'].split('/')
            # 生成内容
            ctx, msg_type = self.msg_type_dict['/'.join(k[3:])](request)
            # 生成消息头和类别码
            hex_msg = pack("<BBHBBLBB",
                           0x21,  # 协议类型
                           0x10,  # 协议版本
                           len(ctx) + 14,  # 报文长度
                           0x0B,  # 消息头长度
                           msg_type,  # 报文类型
                           int(request['msg_id']),  # 报文流水
                           0x00,  # 预留
                           u01_reverse[k[2]],  # 设备u01
                           ) + ctx + b'\x11'
            # 追加校验
            _sum = 0
            for i in hex_msg:
                _sum += i
            _sum = (_sum & 0xff).to_bytes(1, "little")
            hex_msg = hex_msg + _sum
            return hex_msg
        except Exception as e:
            print('错误', e)
            return b'\xFF'


if __name__ == '__main__':
    yrcoder = YRDecoder()
    print("=====================发射控制指令===================================")
    msg_t1 = b'\x12\x10\x18\x00\x0b\x10\x01\x00\x00\x00\x00\x62\x21\x00\x71\x02\x2e\x14\x00\x07\x06\x16\x11\xc2'
    res = yrcoder.decode(msg_t1)
    cb_json = {
        "msg_id": "1",
        "topic": '/domain/vehicle/control',
        "control_cb": "121",
        "time": "22,6,7,0,20,46,625"
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("================航路规划======================================================")
    msg_t6 = b'\x12\x10\xb5\x00\x0b\x14\x02\x00\x00\x00\x00\x62\xc0\x00\x00\x01\xf7\x42\x12\x16\x8a\x26\x3d\x05\x0a\x00\x00\x00' \
             b'\x02\xa8\xe4\x12\x16\x50\x4d\x40\x05\x14\x00\x00\x00\x03\xa8\xe4\x12\x16\xbd\x4e\x43\x05\x1e\x00\x00\x00\x04\x3d\xbc' \
             b'\x12\x16\x1f\xd2\x45\x05\x28\x00\x00\x00\x05\x9a\x9e\x13\x16\x25\x1a\x48\x05\x32\x00\x00\x00\x06\x45\x5b\x15\x16\x69' \
             b'\x90\x48\x05\x3c\x00\x00\x00\x07\x06\x81\x17\x16\x21\x70\x47\x05\x46\x00\x00\x00\x08\x75\x0a\x18\x16\x4f\xe8\x45\x05' \
             b'\x50\x00\x00\x00\x09\x36\xf2\x17\x16\xe5\xae\x43\x05\x5a\x00\x00\x00\x0a\xc4\x68\x17\x16\x49\x9a\x41\x05\x64\x00\x00' \
             b'\x00\x0b\x68\xe7\x16\x16\x1b\x59\x3f\x05\x6e\x00\x00\x00\x0c\x6d\x6b\x15\x16\x3e\x47\x3e\x05\x78\x00\x00\x00\x42\x02' \
             b'\x39\x14\x00\x07\x06\x16\x11\xf2'
    res = yrcoder.decode(msg_t6)

    cb_json = {
        "msg_id": '2',
        "topic": '/domain/vehicle/track/planning',
        "time": "22,6,7,0,20,46,625",
        "seq": "12",
        "status": "1"
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("================光电载荷====================================================")
    # msg_t9 = b'\x12\x10\x1d\x00\x0b\x18\x03\x00\x00\x00\x00\x62\x00\x99\x0f\x04\x03\x02\x01\xfa\x00\x01\x15\x00\x07\x06\x16\x11\xbd'
    msg_t9 = b'\x12\x10\x1a\x00\x0b\x18\x05\x00\x00\x00\x00\x62\x00\x99\x08\x01\xfa\x00\x01\x15\x00\x07\x06\x16\x11\xac'
    res = yrcoder.decode(msg_t9)
    cb_json = {
        "msg_id": '2',
        "topic": '/domain/vehicle/mission/planning/cb',
        "time": "22,6,7,0,20,46,625",
        "seq": "12",
        "status": "1"
    }

    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("================链路规划====================================================")
    msg_t12 = b'\x12\x10\x1c\x00\x0b\x1c\x04\x00\x00\x00\x00\x62\x00\x01\x04\x03\x02\x01\x51\x01\x04\x15\x00\x07\x06\x16\x11\x75'
    res = yrcoder.decode(msg_t12)
    cb_json = {
        "msg_id": '2',
        "topic": '/domain/vehicle/link/planning/cb',
        "time": "22,6,7,0,20,46,625",
        "seq": "12",
        "status": "1"
    }

    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("=================图像信息=====================================================")
    msg_t15 = b'\x12\x10\x16\x00\x0b\x20\x2d\x00\x00\x00\x00\x62\x39\x03\x24\x2d\x0d\x07\x06\x16\x00\xaf'
    res = yrcoder.decode(msg_t15)

    cb_json = {
        "msg_id": '2',
        "topic": '/domain/vehicle/image/cb',
        "time": "22,6,7,0,20,46,625",
        "length": "12",
        "seq": "1",
        "num": "10",
        "data": "222222222222"
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("=================视频信息=====================================================")
    msg_t18 = b'\x12\x10\x16\x00\x0b\x24\x31\x00\x00\x00\x00\x62\x46\x02\x12\x33\x0d\x07\x06\x16\x00\xb7'
    res = yrcoder.decode(msg_t18)

    cb_json = {
        "msg_id": '2',
        "topic": '/domain/vehicle/video/cb',
        "time": "22,6,7,0,20,46,625",
        "rtsp": "rtsp://192.168.1.1/aaa"
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("==================航路轨迹====================================================")
    msg_t21 = b'\x12\x10\x15\x00\x0b\x28\x34\x00\x00\x00\x00\x62\xc4\x01\x07\x3b\x0d\x07\x06\x16\x37'
    res = yrcoder.decode(msg_t21)

    cb_json = {
        "msg_id": '2',
        "topic": '/domain/dji/track/cb',
        "time": "22,6,7,0,20,46,625",
        "num": "2",
        "airline":
            [
                {
                    "longitude": "119.505238",
                    "latitude": "32.197260",
                    "time": "0"
                },
                {
                    "longitude": "119.505082",
                    "latitude": "32.199572",
                    "time": "10"
                }
            ]
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())
    print("================遥控指令======================================================")
    msg_t24 = b'\x12\x10\x16\x00\x0b\x2c\x28\x00\x00\x00\x00\x62\x02\xc4\x01\x07\x3b\x0d\x07\x06\x16\x32'
    res = yrcoder.decode(msg_t24)

    cb_json = {
        "msg_id": '2',
        "topic": '/domain/dji/control/cb',
        "time": "22,6,7,0,20,46,625",
        "seq": "5",
        "sail_switch_command": "1",
        "sail_control_command": "1",
        "link_switch_command": "2",
        "link_frequency": "2400000",
        "catogary_seq": "77",
        "mission_device_switch_control": "1",
        "mission_device_mode": "2",
        "mission_device_param": "02",
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("================遥测指令======================================================")
    msg_t26 = b'\x12\x10\x15\x00\x0b\x30\x29\x00\x00\x00\x00\x62\xc4\x01\x07\x3b\x0d\x07\x06\x16\x34'
    res = yrcoder.decode(msg_t26)

    cb_json = {
        "msg_id": '2',
        "topic": '/domain/dji/telemetry/cb',
        "time": "22,6,7,0,20,46,625",
        "longitude": "119.505238",
        "latitude": "32.197260",
        "speed": "10.5",
        "altitude": "100",
        "yaw": "90.00",
        "mission_device_switch_control": "04",
        "mission_device_param": "01",
        "link_status": "01"
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    print("================平台返航信息======================================================")
    msg_t26 = b'\x12\x10\x16\x00\x0b\x34\x40\x00\x00\x00\x00\x62\x01\xc4\x01\x07\x3b\x0d\x07\x06\x16\x51'
    res = yrcoder.decode(msg_t26)

    cb_json = {
        "msg_id": '2',
        "topic": '/domain/dji/return/cb',
        "time": "22,6,7,0,20,46,625",
        "seq": "05",
        "target_longitude": "119.505238",
        "target_latitude": "32.197260",
        "num": "2",
        "airline":
            [
                {
                    "longitude": "119.505238",
                    "latitude": "32.197260",
                    "time": "0"
                },
                {
                    "longitude": "119.505082",
                    "latitude": "32.199572",
                    "time": "10"
                }
            ]
    }
    res1 = yrcoder.encode(cb_json)
    print(res)
    print(res1.hex())

    cb_json = {"mission_device_param": "0", "link_status": "1", "altitude": 30.64934539794922, "msg_id": "41", "mission_device_switch_control": "0", "longitude": 119.51259847939947, "topic": "/domain/vehicle/telemetry/cb", "time": "22,07,18,22,30,24,891", "latitude": 32.20360857970081, "speed": 0.0, "yaw": -0.6128692030906677}
    res = yrcoder.encode(cb_json)
    print(res)
    print(res.hex())
