import nltk

resources = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]
print("Downloading NLTK resources...")
for r in resources:
    try:
        nltk.download(r, quiet=False)
        print(f"Downloaded {r}")
    except Exception as e:
        print(f"Failed {r}: {e}")
print("Done.")
