import json

def main():
    path = "monkey.json"
    data = json.load(path.read()
    print(data.keys())
    for key, value in data:
        if(key == "id"):
            print("run: "+value)


if __name__ == '__main__':
    main()

