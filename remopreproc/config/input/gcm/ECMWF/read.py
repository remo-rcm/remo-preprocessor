import yaml


with open('era5.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    print(data)

