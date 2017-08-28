import csv, json, sys, os

""" Simple script to format the university CSV to JSON for the website """


def convert(filename):
    # open and create all necessary files
    csvfile = open(filename, 'r')
    jsonfile = open('data.json', 'w')

    # fieldnames for JSON
    fieldnames = ("rank", "name", "website")
    # reader to print to file
    reader = csv.DictReader(csvfile, fieldnames)

    # counter
    i = 0

    # write the first JSON array, surrounded by object
    jsonfile.write("{\"universities\": [\n")

    for row in reader:

        if i != 0:
            jsonfile.write(',\n')

        # dump the contents
        json.dump(row, jsonfile, sort_keys=True, indent=4)
        i = i + 1

    # close array and object
    jsonfile.write('\n]}')

    print("Finished converting.")


def main(argv):
    # Check if there are any arguments
    if (len(argv) < 1):
        # promt user for file
        file = input("No file arguments found.\nEnter filename: ")
    else:
        # Check for help
        if (argv[0] == "-h"):
            print("Usage: python csv2json.py file-to-convert.csv")
            print("Or")
            print("Usage: python csv2json.py")
            print("The latter will bring up a promt to enter a file name.")
            print("If the file does not exist, the script will exit.")

            return
        else:
            # set the file to be converted
            file = argv[0]

    # Convert the file
    convert(file)


# Run the script
if __name__ == "__main__":
    # Pass all arguments into the script
    main(sys.argv[1:])