from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import argparse
import logging



if __name__ =='__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--id', dest='id', type=str, required=True)
    parser.add_argument('--pw', dest='pw', type=str, required=True)
    parser.add_argument('--malware-path', dest='malware_path', type=str, default='./')
    parser.add_argument('--dest', dest='dest', type=str, default='result')


    args = parser.parse_args()

    id = args.id
    pw = args.pw
    path = args.malware_path

    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[ %(levelname)s | %(filename)s: %(lineno)s] %(asctime)s > %(message)s')
    file_handler = logging.FileHandler('log.log')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    if not os.path.exists('{0}/{1}'.format(path, args.dest)):
        os.makedirs('{0}/{1}'.format(path, args.dest))

    chrome_options = Options()

    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  # linux only
    # chrome_options.add_argument("--headless")


    with webdriver.Chrome('./chromedriver', options=chrome_options) as driver:
        driver.implicitly_wait(60)
        ############################### login #####################################
        url = 'https://app.any.run'
        driver.get(url)
        driver.save_screenshot('test.png')
        driver.find_element_by_id('newTaskBtn').click()

        logger.info('Try to login to anyrun ({0})...'.format(url))
        driver.find_element_by_id('at-field-username_and_email').send_keys(id)
        driver.find_element_by_id('at-field-password').send_keys(pw)
        driver.find_element_by_id('at-btn').click()
        time.sleep(5)
        ############################### login #####################################

        for malware in os.listdir(path):
            if not malware.endswith('.exe'):
                continue
            try:
                driver.find_element_by_id('newTaskBtn').click()
            except:
                logger.exception('Failed to login. Please check id and password.')

            logger.info('Login Success. Now creating new task with malware {0}'.format(malware))
            driver.find_element_by_id('file').send_keys('{0}/{1}'.format(path, malware))
            driver.find_element_by_id('runNewTask').click()

            try: # to avoid cookie agreement
                driver.implicitly_wait(10)
                time.sleep(1)
                driver.find_element_by_id('publicWarningAgree').click()
                logger.info('Cookie agreement detected. now avoiding by click agree button.')
            except:
                logger.info('Cookie agreement not detected.')

            driver.implicitly_wait(600) # waiting for maximum 10 mins to process complete
            logger.info('set implicitly time to 10 min. waiting for task has been done')
            driver.find_element_by_id('openMitre').click()
            logger.info('Task all done. now parsing Mitre information.')

            driver.implicitly_wait(60)
            logger.info('set implicitly time to 1 min.')
            try:
                results = list()
                for box in driver.find_elements_by_class_name('box.active'): # parse threat box
                    box.click()
                    results.append(driver.find_element_by_class_name('text-center').text + '\n')
                    results.append(driver.find_element_by_class_name('description').text + '\n\n\n')
                    driver.find_element_by_class_name('close-modal.closeAttackModal').click()

                try:
                    if results:
                        with open('{0}/{1}/{2}.txt'.format(path, args.dest, malware), 'w') as f:
                            for result in results:
                                f.writelines(result.encode('utf-8'))
                except Exception as e:
                    logger.exception('An error occurred Error : {0}'.format(e))
                    logger.exception('results value : {0}'.format(results))
                    raise ValueError('Result value not matched')


                    logger.info('Success to write Mitre information to {0}/{1}/{2}'.format(path, args.dest, malware))

            except Exception as e:
                logger.exception('An error occurred Error : {0}'.format(e))



