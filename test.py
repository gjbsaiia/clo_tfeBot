import json

def main():
    path = "monkey.json"
    with open(path) as son:
        all = json.load(son)
    data = all["data"]
    for run in data:
        for key in run:
            if(key == "id"):
                print("run: "+run[key])
            if(key == "attributes"):
                attributes = run[key]
                for key in attributes:
                    if(key == "status"):
                        print("status: "+attributes[key])
            if(key == "links"):
                links = run[key]
                for key in links:
                    print("link to run: "+links[key])
                print()


if __name__ == '__main__':
    main()
