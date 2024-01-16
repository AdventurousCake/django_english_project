# corrections from full resp
        """[ { 'longDescription': 'A word was not spelled correctly',
            'mistakeText': 'i',
            'shortDescription': 'Spelling Mistake',
            'suggestions': [ { 'category': 'Spelling',
            'definition': 'refers to the speaker or writer',
            'text': 'I'}]},

            { 'longDescription': 'Unknown word - no suggestions available',
            'mistakeText': 'django',
            'shortDescription': 'Possible Spelling Mistake',
            'suggestions': []},
        """


# full resp
        """
        {'id': '8710fb7c-97a8-4545-bd9d-f3b90f33a6e4', 'language': 'eng',
             'text': "We'vereceivedanewproposalfortheproject.Iwillkeepyouinformedabouthowthingsgo.",
             'engine': 'Ginger', 'truncated': False, 'timeTaken': 473, 

             'corrections': [
                {'group': 'AutoCorrected', 'type': 'Grammar', 'shortDescription': 'GrammarMistake',
                 'longDescription': 'Errorinformingorapplyingthepresentperfecttense', 'startIndex': 0, 'endIndex': 12,
                 'mistakeText': "We'vereceive", 'correctionText': "We'vereceived",
                 'suggestions': [{'text': "We'vereceived", 'category': 'Verb'}]}],

             'sentences': [{'startIndex': 0, 'endIndex': 44, 'status': 'Corrected'},
                           {'startIndex': 46, 'endIndex': 90, 'status': 'Corrected'}], 'autoReplacements': [],
             'stats': {'textLength': 91, 'wordCount': 18, 'sentenceCount': 2, 'longestSentence': 45}}"""