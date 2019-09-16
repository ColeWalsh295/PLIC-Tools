import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
from matplotlib import gridspec
import matplotlib.pyplot as plt
plt.style.use('seaborn-white')
import Valid_Matched
import Scoring

def GenerateGraph(OtherPreFile, OtherPostFile, Level, ID, Weightsdf, **Dataframes):
    global NValidPost, N_Other, dfYour_Post

    dfOther_Pre = pd.read_csv(OtherPreFile)

    dfOther_Post = pd.read_csv(OtherPostFile)

    dfOther = pd.concat([dfOther_Pre, dfOther_Post], axis = 0, join = 'inner').reset_index(drop = True) # Collect all data together for CFA model building

    dfOther_Pre_Level = dfOther_Pre[dfOther_Pre['Course_Level'] == Level].reset_index(drop = True) # Filter out pre cumulative data by course level
    dfOther_Pre_Level = dfOther_Pre_Level.assign(Survey = 'PRE', Data = 'Other')

    dfOther_Post_Level = dfOther_Post[dfOther_Post['Course_Level'] == Level].reset_index(drop = True) # Filter out post cumulative data by course level
    dfOther_Post_Level = dfOther_Post_Level.assign(Survey = 'POST', Data = 'Other')
    N_Other = len(dfOther_Post_Level)

    if('MID' in Dataframes.keys()): # Build class dataframe when 3 surveys are given
        NValidPre, NValidMid, NValidPost, dfYour_Pre, dfYour_Mid, dfYour_Post = Valid_Matched.ValMat(PRE = Dataframes['PRE'], MID = Dataframes['MID'], POST = Dataframes['POST'])

        dfYour_PreS = Scoring.CalcScore(dfYour_Pre, Weightsdf)
        dfYour_PreS = dfYour_PreS.assign(Survey = 'PRE', Data = 'Yours', Class_ID = ID)

        dfYour_MidS = Scoring.CalcScore(dfYour_Mid, Weightsdf)
        dfYour_MidS = dfYour_MidS.assign(Survey = 'MID', Data = 'Yours', Class_ID = ID)

        dfYour_PostS = Scoring.CalcScore(dfYour_Post, Weightsdf)
        dfYour_PostS = dfYour_PostS.assign(Survey = 'POST', Data = 'Yours', Class_ID = ID)

        df_Concat = pd.concat([dfYour_PreS, dfYour_MidS, dfYour_PostS, dfOther_Pre_Level, dfOther_Post_Level], axis = 0, join = 'inner').reset_index(drop = True) # Collect all data to be plotted into one dataframe
    elif('PRE' in Dataframes.keys()): # Build class dataframe when 2 surveys are given
        NValidPre, NValidPost, dfYour_Pre, dfYour_Post = Valid_Matched.ValMat(PRE = Dataframes['PRE'], POST = Dataframes['POST'])

        dfYour_PreS = Scoring.CalcScore(dfYour_Pre, Weightsdf)
        dfYour_PreS = dfYour_PreS.assign(Survey = 'PRE', Data = 'Yours', Class_ID = ID)

        dfYour_PostS = Scoring.CalcScore(dfYour_Post, Weightsdf)
        dfYour_PostS = dfYour_PostS.assign(Survey = 'POST', Data = 'Yours', Class_ID = ID)

        df_Concat = pd.concat([dfYour_PreS, dfYour_PostS, dfOther_Pre_Level, dfOther_Post_Level], axis = 0, join = 'inner').reset_index(drop = True) # Collect all data to be plotted into one dataframe
    else: # Build class dataframe when only 1 survey is given
        NValidPost, dfYour_Post = Valid_Matched.ValMat(POST = Dataframes['POST'])

        dfYour_PostS = Scoring.CalcScore(dfYour_Post, Weightsdf)
        dfYour_PostS = dfYour_PostS.assign(Survey = 'POST', Data = 'Yours', Class_ID = ID)

        df_Concat = pd.concat([dfYour_PostS, dfOther_Pre_Level, dfOther_Post_Level], axis = 0, join = 'inner').reset_index(drop = True) # Collect all data to be plotted into one dataframe

    df_Factors = Scoring.CalcFactorScores(dfOther, df_Concat) # Get factor scores for yours and other classes
    df_Concat = pd.concat([df_Concat, df_Factors], axis = 1, join = 'inner') # Merge the factor scores back with the question scores dataframe for yours and other classes

    GenerateTotalScoresGraph(df_Concat)
    GenerateQuestionsGraph(df_Concat)

    if('PRE' in Dataframes.keys()):
        dfYour_Pre['Course_Level'] = Level # Append the new pre data to the historical data for future use
        dfOther_Pre = pd.concat([dfOther_Pre, dfYour_PreS], join = 'inner', axis = 0)
        # dfOther_Pre.to_csv(OtherPreFile, index = False)

        dfYour_Post['Course_Level'] = Level # Append the new post data to the historical data for future use
        dfOther_Post = pd.concat([dfOther_Post, dfYour_PostS], join = 'inner', axis = 0)
        # dfOther_Post.to_csv(OtherPostFile, index = False)

        if('MID' in Dataframes.keys()):
            return NValidPre, NValidMid, NValidPost, dfYour_Pre, dfYour_Mid, dfYour_Post
        else:
            return NValidPre, NValidPost, dfYour_Pre, dfYour_Post
    else:
        return NValidPost, dfYour_Post

def GenerateTotalScoresGraph(df): # Generate main total scores graph that includes factor scores in a 2x2 layout
    df = df.loc[:, ['Data', 'Survey', 'models', 'methods', 'actions', 'TotalScores']]

    matplotlib.rcParams.update({'font.size': 16, 'font.family': "sans-serif", 'font.sans-serif': "Arial"})
    fig, axes = plt.subplots(2, 2, figsize = (12, 9))

    y_max = df.loc[:, 'models':].apply(max)
    if('MID' in list(df['Survey'])): # Indicate order of surveys based on whether to include a mid survey level
        Survey_order = ['PRE', 'MID', 'POST']
    else:
        Survey_order = ['PRE', 'POST']

    plt.sca(axes[0, 0])
    sns.boxplot(x = 'Data', y = 'models', hue = 'Survey', hue_order = Survey_order, data = df, linewidth = 0.5, palette = {'PRE':'#ece7f2', 'MID':'#a6bddb', 'POST':'#2b8cbe'})
    plt.xticks((0, 1), ('Your Class', 'Other Classes'))
    plt.xlabel('')
    plt.ylabel('Score')
    plt.title('Evaluating models scale')
    axes[0, 0].legend(bbox_to_anchor = (0, 1.12))

    plt.sca(axes[0, 1])
    sns.boxplot(x = 'Data', y = 'methods', hue = 'Survey', hue_order = Survey_order, data = df, linewidth = 0.5, palette = {'PRE':'#ece7f2', 'MID':'#a6bddb', 'POST':'#2b8cbe'})
    plt.xticks((0, 1), ('Your Class', 'Other Classes'))
    plt.xlabel('')
    plt.ylabel('Score')
    plt.title('Evaluating methods scale')
    axes[0, 1].legend().remove()

    plt.sca(axes[1, 0])
    sns.boxplot(x = 'Data', y = 'models', hue = 'Survey', hue_order = Survey_order, data = df, linewidth = 0.5, palette = {'PRE':'#ece7f2', 'MID':'#a6bddb', 'POST':'#2b8cbe'})
    plt.xticks((0, 1), ('Your Class', 'Other Classes'))
    plt.xlabel('')
    plt.ylabel('Score')
    plt.title('Suggesting follow-ups scale')
    axes[1, 0].legend().remove()

    plt.sca(axes[1, 1])
    sns.boxplot(x = 'Data', y = 'TotalScores', hue = 'Survey', hue_order = Survey_order, data = df, linewidth = 0.5, palette = {'PRE':'#ece7f2', 'MID':'#a6bddb', 'POST':'#2b8cbe'})
    plt.xticks((0, 1), ('Your Class', 'Other Classes'))
    plt.xlabel('')
    plt.ylabel('Score')
    plt.title('Total Scores')
    axes[1, 1].legend().remove()

    plt.tight_layout()
    fig.savefig('FactorsLevel.png')
    plt.close()
    plt.clf()

def GenerateQuestionsGraph(df):
    df_melt = pd.melt(df, id_vars = ['Data', 'Survey'], value_vars = ['Q1Bs', 'Q1Ds', 'Q1Es', 'Q2Bs', 'Q2Ds', 'Q2Es', 'Q3Bs', 'Q3Ds', 'Q3Es', 'Q4Bs'])

    dfYours = df_melt.loc[df_melt['Data'] == 'Yours', :]
    dfOther = df_melt.loc[df_melt['Data'] == 'Other', :]

    matplotlib.rcParams.update({'font.size': 16, 'font.family': "sans-serif", 'font.sans-serif': "Arial"})
    fig, axes = plt.subplots(1, 2, figsize = (12, 9))

    plt.sca(axes[0])
    sns.boxplot(x = 'value', y = 'variable', hue = 'Survey', data = dfYours, linewidth = 0.5, palette = {'PRE':'#ece7f2', 'MID':'#a6bddb', 'POST':'#2b8cbe'})
    plt.xlabel('Score')
    plt.ylabel('Question')
    plt.yticks(range(10), ('Q1B', 'Q1D', 'Q1E', 'Q2B', 'Q2D', 'Q2E', 'Q3B', 'Q3D', 'Q3E', 'Q4B'))
    plt.title('Your Class (N = {0})'.format(len(dfYour_Post.index)))

    plt.sca(axes[1])
    sns.boxplot(x = 'value', y = 'variable', hue = 'Survey', data = dfOther, linewidth = 0.5, palette = {'PRE':'#ece7f2', 'POST':'#2b8cbe'})
    plt.xlabel('Score')
    plt.title('Similar Classes (N = {0})'.format(N_Other))

    if('PRE' in list(dfYours['Survey'])): # Get legend from axes that has the most bars
        axes[0].legend(bbox_to_anchor = (-0.08, 1.05))
        axes[1].legend().remove()
    else:
        axes[0].legend().remove()
        axes[1].legend(bbox_to_anchor = (1.02, 1.05))

    axes[1].get_shared_y_axes().join(axes[0], axes[1])
    axes[1].set_ylabel('')
    axes[1].set_yticklabels([])

    plt.tight_layout()
    fig.savefig('QuestionsLevel.png', orientation = 'landscape')
    plt.close()
    plt.clf()