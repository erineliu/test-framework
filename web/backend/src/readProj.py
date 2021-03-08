import pandas as pd 


def getProjList(path):
    df = pd.read_csv(path)  
    #print(df.to_json(orient="records"))  ## to Json
    return df.to_dict(orient="records")



if __name__ == "__main__":
    pass
