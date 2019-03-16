def cleanNumber(inputStr):
    try:
        return float(inputStr)
    except:
        # Non numeric
        firstWord = inputStr.split(" ")[0].replace(",", "")
        try:
            return float(firstWord)
        except:
            pass
    return np.nan