from math import log10
import index

k1 = 1.2
k2 = 100
b = 0.75


def calcBM25Scores(termCount, myindex, query, coder):
    """BM25 Retrieval Model"""
    
    notTerms = query.get('NOT', [])
    andTerms = query.get('AND', [])
    orTerms = query.get('OR', [])

    termIndex = {}
    docids = []
    # Select all docs from OR and AND terms
    terms = orTerms[:]
    terms.extend(andTerms)
    for term in terms:
        tc = index.getTermContent(myindex, term, coder)
        termIndex[term] = tc
        docids.extend(tc.get('docs', []).keys())
    
    # Remove docs from NOT    
    exdocids = []
    for term in notTerms:
        tc = index.getTermContent(myindex, term, coder)
        exdocids.extend(tc.get('docs', []).keys())
    
    # Calc term frequency in query
    qFreq = {}
    for term in terms:
        qFreq[term] = qFreq.setdefault(term, 0) + 1
        
    scores = []
    for docID in docids:
        if docID in exdocids:
            continue

        K = k1 * ((1 - b) + (b * termCount.get(docID) / termCount.get('average')))
        docScore = 0.0
        for term in terms:
            docScore = log10((termCount['totalDocs'] - termIndex[term].get('count', 0) + 0.5)
                             / (termIndex[term].get('count', 0) + 0.5))
            
            docScore = docScore * ((k1 + 1) * termIndex[term]['docs'].get(docID, 0.0)) / (K + termIndex[term]['docs'].get(docID, 0.0))
            
            docScore = docScore * (((k2 + 1) * qFreq[term]) / (k2 + qFreq[term]))
            
        scores.append([docID, docScore])	
    return scores