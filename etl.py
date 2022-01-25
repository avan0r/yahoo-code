import argparse
import csv
import json
import yaml
from dict2xml import dict2xml

#Set up the argument parser
def set_up_parser():

    parser = argparse.ArgumentParser(description="Process data")

    parser.add_argument("-i", dest='input_file', required=True, help="The input file with data" )
    parser.add_argument("-f", dest='out_format', choices=['json', 'yaml', 'xml', 'stdout'], default='stdout', help="Choose output format from JSON, XML, or YAML")
    parser.add_argument("-o", dest='outfile', help="Optional: Choose output file")
    parser.add_argument("-q", action='store_true', help="Prints to file only, no stdout")

    return parser

# Read the file and populate values data
def read_file(filename):

    f = open(filename, 'r')
    dreader = csv.DictReader(f)


    values = {}
    line_count = 0

    # Global min/max
    values['global_values'] = {'min': 100,
                    'max': 0,
                    'total': 0,
                    'avg': 0,
                    'count': 0
                    }

    # Init header as keys
    for host in dreader.fieldnames:
        values[host] = {}

    # Iterate rows
    for row in dreader:

        # Set basline of data from first row
        if line_count == 0:

            for host in row.keys():
                if host == 'Date / Time':
                    pass

                elif row[host]:
                    values[host]['avg'] = float(row[host])
                    values[host]['min'] = float(row[host])                     
                    values[host]['max'] = float(row[host])
                    values[host]['total'] = float(row[host])
                    values[host]['count'] = 1
                else:
                    values[host]['avg'] = 0.0
                    values[host]['total'] = 0
                    values[host]['count'] = 0

        # Process other rows
        if line_count > 0:

            for host in row.keys():
                
                if host == 'Date / Time':
                    pass

                elif row[host]:

                    # Add to total and count data points
                    values[host]['total'] += float(row[host])
                    values[host]['count'] += 1
                    values[host]['avg'] = values[host]['total'] / values[host]['count']

                    # Calculate global values
                    values['global_values']['max'] = max(values['global_values']['max'], float(row[host]))
                    values['global_values']['min'] = min(values['global_values']['min'], float(row[host]))
                    values['global_values']['total'] += float(row[host])
                    values['global_values']['count'] += 1
                    values['global_values']['avg'] = values['global_values']['total'] /  values['global_values']['count']

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

    # Delete time because it doesnt really matter
    del values['Date / Time'] 

    return values

# Print data based on type selected
def print_data(data, out_format):

    if out_format == 'json':
        print(json.dumps(data))

    elif out_format == 'xml':
        print(dict2xml(data))

    elif out_format == 'yaml':
        print(yaml.dump(data))

    else:
        print(data)
        for host in data.keys():
            print("host {} -- min {}, max {}, avg {:.2f}, datapoints {}".format(host, data[host]['min'], data[host]['max'], data[host]['avg'], data[host]['count']))

# Write to file with type selected
def write_to_file(data, out_format, outfile):

    if out_format == 'json':
        with open(outfile, 'w') as f:
            f.write(json.dumps(data))

    elif out_format == 'xml':
        with open(outfile, 'w') as f:
            f.write(dict2xml(data))

    elif out_format == 'yaml':
        with open(outfile, 'w') as f:
            f.write(yaml.dump(data))
    

if __name__ == '__main__':

    parser = set_up_parser()
    args = parser.parse_args()

    data = read_file(args.input_file)

    if args.outfile:
        write_to_file(data, args.out_format, args.outfile)

    if not args.q:    
        print_data(data, args.out_format)
