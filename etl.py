import argparse
import csv
import json
import yaml
from dict2xml import dict2xml

#Set up the argument parser
def set_up_parser():

    parser = argparse.ArgumentParser(description="Process data")

    parser.add_argument("-f", dest='input_file', required=True, help="The input file with data" )
    parser.add_argument("-o", dest='out_format', choices=['json', 'yaml', 'xml', 'stdout'], default='stdout')

    return parser

# Read the file and populate values data
def read_file(filename):

    f = open(filename, 'r')
    dreader = csv.DictReader(f)


    values = {}
    line_count = 0

    # Init header as keys
    for host in dreader.fieldnames:
        values[host] = {}

    # Iterate rows
    for row in dreader:

        # Set basline of data from first row
        if line_count == 0:

            for host in row.keys():
                if row[host]:
                    values[host]['avg'] = float(row[host])
                    values[host]['min'] = float(row[host])                     
                    values[host]['max'] = float(row[host])
                    values[host]['count'] = 1
                else:
                    values[host]['avg'] = 0.0
                    values[host]['count'] = 0

        # Process other rows
        if line_count > 0:

            for host in row.keys():
                
                if row[host]:

                    # Add to total and count data points
                    values[host]['avg'] += float(row[host])
                    values[host]['count'] += 1

                    # Keep track of min/max, catch error if there is no value
                    try:
                        values[host]['max'] = max(float(row[host]), values[host]['max'])
                    except (KeyError):
                        values[host]['max'] = float(row[host])
                    
                    try:
                        values[host]['min'] = min(float(row[host]), values[host]['min'])
                    except (KeyError):
                        values[host]['min'] = float(row[host])

        # Increase row count
        line_count += 1
        
    return values

# Print data based on type selected
def output_data(data, out_format):

    if out_format == 'json':
        print(json.dumps(data))

    elif out_format == 'xml':
        print(dict2xml(data))

    elif out_format == 'yaml':
        print(yaml.dump(data))

    else:
        
        for host in data.keys():
            print("host {} -- min {}, max {}, avg {:.2f}, datapoints {}".format(host, data[host]['min'], data[host]['max'], data[host]['avg']/data[host]['count'], data[host]['count']))


if __name__ == '__main__':

    parser = set_up_parser()
    args = parser.parse_args()

    data = read_file(args.input_file)

    output_data(data, args.out_format)

