import pandas as pd

df_pos = pd.read_csv('word_list/positive_words.csv')
df_neg = pd.read_csv('word_list/negative_words.csv')

if __name__ == "__main__":
    df_pos = df_pos.assign(score=1)
    df_pos.to_csv('word_list/positive_words.csv', index=False)
    df_neg = df_neg.assign(score=-1)
    df_neg.to_csv('word_list/negative_words.csv', index=False)
