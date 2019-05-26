"""
Villa Astrid Json Library

"""
def float_to_json(zone, sensor, value, float_format, remark):
    JsonString = '{\"Z\":\"'
    JsonString += zone + '\",'
    JsonString += '\"S\":\"'
    JsonString += sensor + '\",'
    JsonString += '\"V\":'
    JsonString += float_format.format(value)
    JsonString += ',\"R\":\"'
    JsonString += remark
    JsonString += '\"}'
    return(JsonString)

def json_fix(s):
    n = s.find(':')
    s = s[n+1:]
    if s[0] == '"':
        s = s[1:-1]
    return s	

def expand_attr(s):
    jattr = ''
    if s[0] == '"' and s[2] == '"':
        if s[1] == 'Z':
            jattr = 'Zone'
        elif s[1] == 'S':
            jattr = 'Sensor'
        elif s[1] == 'V':
            jattr = 'Value'
        elif s[1] == 'R':
            jattr = 'Remark'
    return jattr

def parse_str(radio_str):
    # radio_str = '{"Z":"OD_1","S":"Hum","V":99.90,"R":""}'
    rm = {'Zone': '', 'Sensor': '', 'Value': '', 'Remark': ''}
    if radio_str.endswith('}') and radio_str.startswith('{'):
        #print('JSON is OK')
        rs = radio_str[1:-1].split(',')
        # print(rs)
        for i in range(len(rm)):
            attr = expand_attr(rs[i])
            # print(attr)
            if attr in rm:
                # print(json_fix(rs[i]))
                s1 = json_fix(rs[i])
                if attr == 'Sensor':
                    pass
                    # s1 = sensor_fix4(s1)

                rm[attr] = s1
    #print(rm)
    return rm
