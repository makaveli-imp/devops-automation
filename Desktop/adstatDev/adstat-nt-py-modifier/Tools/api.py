import json



class Api():

    def xpath_api(driver):
        id = 0
        url = driver.current_url
        if 'assabah' in url:
            id = 1
        elif 'alakhbar' in url:
            id = 2
        elif 'hespress' in url:
            id = 3
        elif 'hibapress' in url:
            id = 4
        elif 'lnt.ma' in url:
            id = 5
        elif 'moteur.ma' in url:
            id = 6
        elif 'lintermediaire.ma' in url:
            id = 7
        elif 'aabbir.com' in url:
            id = 8
        elif 'ariffino.net' in url:
            id = 9
        elif 'almaghreb24' in url:
            id = 10
        elif '24saa.ma' in url:
            id = 11
        elif 'telquel.ma' in url:
            id  = 12
        elif '2m.ma' in url:
            id = 13
        elif 'akhbarona' in url:
            id = 14
        elif 'ahdath.info' in url:
            id = 15
        elif 'al3omk.com' in url:
            id = 16
        elif 'avito' in  url:
            id = 17
        elif 'chouftv' in url:
            id = 18
        elif 'le2minutes' in url:
            id = 19
        elif 'barlamane' in url:
            id = 20
        elif 'infomediaire' in url:
            id = 21
        elif 'lepointfeminin' in url:
            id = 22
        elif 'hesport' in url:
            id = 23
        elif 'lebrief' in url:
            id = 24
        elif 'ecoactu.ma' in url:
            id = 25
        elif 'alwadifa-maroc' in url:
            id = 26
        elif 'marocannonces' in url:
            id = 27
        elif 'belpresse' in url:
            id = 28
        elif 'cawalisse' in url:
            id = 29
        elif 'anbaetv.ma' in url:
            id = 30
        elif 'wandaloo' in url:
            id = 31
        elif 'lopinion.ma' in url:
            id = 32
        elif 'almountakhab' in url:
            id = 33
        elif 'elbotola' in url:
            id = 34
        elif 'fnh.ma' in url:
            id = 35
        elif 'boursenews' in url:
            id = 36
        elif 'alayam24.com' in url:
            id = 37
        elif 'alyaoum24.com' in url:
            id = 38
        elif 'kifache.com' in url:
            id = 39
        elif 'lobservateur.info' in url:
            id = 40
        elif 'santeplus.ma' in url:
            id = 41
        elif 'lematin.ma' in url:
            id = 42
        elif 'walaw.press' in url:
            id = 43
        else:
            return None
        f = open('Tools/adspath.json')
        sites = json.load(f)
        f.close()
        return sites[str(id)]