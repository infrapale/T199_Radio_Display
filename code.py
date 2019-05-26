"""
T199  3x 14 segm display

"""
import time
import board
import busio as io
import adafruit_ht16k33.segments
import adafruit_bme680
import digitalio
import adafruit_rfm69
# import adafruit_sdcard
# import storage
import neopixel
import va_json as json

i2c = io.I2C(board.SCL, board.SDA)
spi = io.SPI(board.SCK, board.MOSI, board.MISO)
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c, 0x76)
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
cs = digitalio.DigitalInOut(board.D9)
reset = digitalio.DigitalInOut(board.D11)

display1 = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x70)
display2 = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x71)
display3 = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x72)
display = [display1,display2,display3]
for i in range(0,3):
    display[i].print(i)
display[0].print('T199')
display[1].print('TomH')
display[2].print('2019')

RADIO_FREQ_MHZ = 434.0
# Initialze RFM radio
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, RADIO_FREQ_MHZ)
# ino: uint8_t key[] ="VillaAstrid_2003"
e_key = b'\x56\x69\x6c\x6c\x61\x41\x73\x74\x72\x69\x64\x5f\x32\x30\x30\x33'
rfm69.encryption_key = e_key
rec_msg = {'Zone': '', 'Sensor': '', 'Value': '', 'Remark': ''}
sensor_4char = {'T_bmp180': 'TMP2', 'P_bmp180': 'ILMP',
                'H_dht22': 'HUM ', 'T_dht22': 'TMP1',
                'T_Water': 'LAKE', 'Light1': 'LDR1', 'Light2': 'LDR2',
                'Temp2': 'TMP2'}

fall_back_values = [['TUPA','TEMP','0'],['OD_1','Temp','0'],['Dock','T_Water','0'],['Test','Test1','0']]

def sensor_fix4(s):
    if s in sensor_4char:
        s = sensor_4char[s]
    else:
        s = s[0:4]
    return s


def adapt_value_4_char(v):
    if len(v) > 4:
        if '.' in v:
            return v[0:5]
        else:
            return v[0:4]
    else:
        return v

# display1 = adafruit_ht16k33.segments.Seg14x4(i2c)

led[0] = (255, 200, 0)
print('Waiting for packets...')

last_time_msg_sent = time.monotonic()
last_meas_rec = time.monotonic()
meas_indx = 0
zone = 'TUPA'

def send_one_meas():
    global meas_indx
    print('Sending one sensor value')
    meas_indx += 1
    if meas_indx == 1:
        # s = float_to_json('TEST', 'TEMP', sensor.temperature, 'C')
        rfm69.send(bytes(json.float_to_json(zone, 'TEMP',
                        sensor.temperature, '{:.1f}', 'C'), 'utf-8'))
    elif meas_indx == 2:
        rfm69.send(bytes(json.float_to_json(zone, 'HUM ',
                        sensor.humidity/100, '{:.0%}',''), 'utf-8'))
    elif meas_indx == 3:
        rfm69.send(bytes(json.float_to_json(zone, 'GAS ',
                        sensor.gas/1000, '{:.0f}', 'kOhm'), 'utf-8'))
    elif meas_indx == 4:
        rfm69.send(bytes(json.float_to_json(zone, 'hPa ',
                        sensor.pressure,  '{:.0f}',''), 'utf-8'))
    else:
        meas_indx = 0
    rfm69.listen()

def show_fallback_meas():
        for i in range(0,3):
             display[i].fill(0)
             display[i].print(adapt_value_4_char(fall_back_values[i][2]))
             # print(adapt_value_4_char(fall_back_values[i][2]))

def collect_fallback(r_msg):
    #print(r_msg['Zone'],r_msg['Sensor'],r_msg['Value'])
    #print(fall_back_values[0:2][0])
    fb_values = len(fall_back_values[0])
    fb_found = False
    for i in range(fb_values+1):
        if r_msg['Zone']==fall_back_values[i][0]:
            for j in range(fb_values+1):
                if r_msg['Sensor']==fall_back_values[j][1]:
                    fb_found = True
                    break
            break
    if fb_found:
        fall_back_values[i][2] = r_msg['Value']
        print(fall_back_values[i][0],fall_back_values[j][1])
    else:
        print('fallback not found')



# test code
test_mode = False
if test_mode:
    test_msg = {'Zone': 'OD_1', 'Sensor': 'Temp', 'Value': '12.3', 'Remark': ''}
    collect_fallback(test_msg)
    while True:
        pass

while True:
    packet = rfm69.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm69.receive(timeout=5.0)

    if packet is None:
        # do scheduled tasks
        if time.monotonic() - last_time_msg_sent > 60:
            last_time_msg_sent = time.monotonic()
            send_one_meas()
        if time.monotonic() - last_meas_rec > 20:
            last_meas_rec = time.monotonic()
            fall_back_values[0][2] = '{:.1f}'.format(sensor.temperature)
            print(fall_back_values[0])
            show_fallback_meas()
        pass
        # print('Received nothing! Listening again...')
    else:
        last_meas_rec = time.monotonic()
        print('Received (raw bytes): {0}'.format(packet))
        packet_text = str(packet, 'ascii')
        print('Received (ASCII): {0}'.format(packet_text))
        rec = '{0}'.format(packet_text)
        rec_msg = json.parse_str(rec)
        collect_fallback(rec_msg)
        #print(rec_msg)
        display[0].fill(0)
        display[0].print(rec_msg['Zone'])
        display[1].fill(0)
        display[1].print(rec_msg['Sensor'])
        display[2].fill(0)
        display[2].print(adapt_value_4_char(rec_msg['Value']))