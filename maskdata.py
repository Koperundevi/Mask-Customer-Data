#import required packages/modules
import csv
import re
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')

#method to replace the list of dict, key with the given value 
def replaceValue(replaceDict, data):
    for row in data:
        for key, value in replaceDict.items():
            row[key] = value if row[key].strip() else row[key]
    return data

#method to mask the customer data
def maskCustomerData(customerData, sensitiveColTyp):
    #initalizing count and totalbilling to calculate the average at the end
    count, totalBilling = 0, 0

    #initialize variable to get the maximum, minimum len/value of name and billing field
    minName, maxName, minBilling, maxBilling = 0, 0, 0, 0

    '''while reading from database, use the dictreader in relationaldb reader with which the below code
    can be reused'''
    maskedData = []
    for row in customerData:
        for key, value in row.items():
            if key in sensitiveColTyp['AlphaNumeric']:
                row[key] = re.sub('[0-9a-zA-Z]', 'X', value) #masking the alphanumeric letters to X
                
                minName = len(value) if (key == 'Name' and len(value)<minName or minName==0) else minName
                maxName = len(value) if key == 'Name' and minName>0 and len(value)>maxName else maxName

            #adding to billing amount to calculate average
            #making the value in average only when the row has values
            elif key in sensitiveColTyp['Numeric'] and value.strip(): 
                count = count + 1
                totalBilling = totalBilling + float(value) 

                minBilling = float(value) if (key == 'Billing' and float(value)<minBilling or minBilling==0) else minBilling
                maxBilling = float(value) if key == 'Billing' and float(value)>maxBilling else maxBilling
        
        maskedData.append(row)

    #get the average value of billing and change the column values
    averageBilling = totalBilling / count
    # in a dict data type, to add any other common values in the future to replace
    replaceDict = {'Billing': averageBilling}
    maskedData = replaceValue(replaceDict, maskedData)

    #log the min max avg value of name and billing
    reportDict = {'minName':minName,
                'maxName':maxName,
                'avgName': (minName+maxName) /2,
                'minBilling':minBilling,
                'maxBilling':maxBilling,
                'avgBilling': (minBilling+maxBilling)/2}

    logger.info('Name: Max. %(maxName)s, Min. %(minName)s, Avg. %(avgName)s\
                \nBilling: Max. %(maxBilling)s, Min. %(minBilling)s, Avg. %(avgBilling)s',
                reportDict)
    return maskedData

#method - csv dict writer
def csvDictWriter(filename, data):
    if data:
        with open(filename+'.csv', 'w', newline='') as csvFile:
            csvWriter = csv.DictWriter(csvFile, fieldnames = data[0].keys())
            csvWriter.writeheader()
            csvWriter.writerows(data)

if __name__ == '__main__':

    #ColumnType for masking
    sensitiveColTyp = {'AlphaNumeric': ['Name','Email'],
    'Numeric': ['Billing']}

    #open customers.csv, should give the complete location if its not in same folder
    customerCsv = open('customers.csv')

    #Read the data in dict data type using csv dict reader
    customerData = csv.DictReader(customerCsv, delimiter=',')

    #mask the customer data
    maskedData = maskCustomerData(customerData, sensitiveColTyp)

    #writing maskedData to csv
    csvDictWriter('masked_clients', maskedData)

    logger.info("Data has been masked and successfully saved to csv")
