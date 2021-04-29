from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time

def get_dhcp_list():
    opts = Options()
    opts.set_headless()
    assert opts.headless 
    browser = Chrome(options=opts)
    browser.get('http://tplinkwifi.net/')
    time.sleep(2)
    user = browser.find_element_by_id("userName")
    user.send_keys('admin')
    passwd = browser.find_element_by_id("pcPassword")
    passwd.send_keys('admin')
    btn = browser.find_element_by_id("loginBtn")
    btn.click()
    time.sleep(2)
    browser.switch_to_frame("frame1")

    btn = browser.find_element_by_id("menu_dhcp")
    btn.click()
    btn = browser.find_element_by_id("menu_dhcpclient")
    btn.click()
    browser.switch_to_default_content()
    browser.switch_to_frame("frame2")
    time.sleep(2)
    tab = browser.find_element_by_id('hostTbl')
    html=tab.get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    data = [ele.text for ele in soup.find_all('td')]

    cl =[]
    ref_dict = {}
    for i in range(int(len(data)/5)):
        j = 5*i
        client = {}
        
        client["idx"],client["name"],client["mac"],client["ip"],client["time"] = (data[j], data[j+1], data[j+2], data[j+3], data[j+4])
        ref_dict[client["name"]] = client["ip"]
        cl.append(client)
    
    return cl,ref_dict


if __name__ == "__main__":
    cl,ref_dict = get_dhcp_list()
    print("Detailed List :  ", cl)
    print("Reference List : ",ref_dict)