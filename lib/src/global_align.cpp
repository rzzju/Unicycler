#include "global_align.h"


#include <seqan/align.h>
#include "semi_global_align.h"



char * fullyGlobalAlignment(char * s1, char * s2,
                            int matchScore, int mismatchScore, int gapOpenScore, int gapExtensionScore,
                            bool useBanding, int bandSize) {

    // Change the sequences to C++ strings.
    std::string sequence1(s1);
    std::string sequence2(s2);

    ScoredAlignment * alignment = fullyGlobalAlignment(sequence1, sequence2,
                                                       matchScore, mismatchScore, gapOpenScore, gapExtensionScore,
                                                       useBanding, bandSize);

    std::string returnString = alignment->getFullString();
    delete alignment;
    return cppStringToCString(returnString);
}

// This function runs a global alignment between two sequences.
ScoredAlignment * fullyGlobalAlignment(std::string s1, std::string s2,
                                       int matchScore, int mismatchScore, int gapOpenScore, int gapExtensionScore,
                                       bool useBanding, int bandSize) {
    long long startTime = getTime();

    Dna5String sequenceH(s1);
    Dna5String sequenceV(s2);

    Align<Dna5String, ArrayGaps> alignment;
    resize(rows(alignment), 2);
    assignSource(row(alignment, 0), sequenceH);
    assignSource(row(alignment, 1), sequenceV);
    Score<int, Simple> scoringScheme(matchScore, mismatchScore, gapExtensionScore, gapOpenScore);

    AlignConfig<false, false, false, false> alignConfig;
    int score;
    if (useBanding) {
        int lowerDiagonal = -bandSize;
        int upperDiagonal = bandSize;
        int lengthDifference = length(s2) - length(s1);

        // If s2 is longer, then we need to expand the lower diagonal a bit.
        if (lengthDifference > 0)
            lowerDiagonal -= lengthDifference;

        // If s1 is longer, then we need to expand the upper diagonal a bit.
        else if (lengthDifference < 0)
            upperDiagonal -= lengthDifference;

        std::cout << "Lower diagonal: " << lowerDiagonal << std::endl; // TEMP
        std::cout << "Upper diagonal: " << upperDiagonal << std::endl; // TEMP
        
        score = globalAlignment(alignment, scoringScheme, alignConfig, lowerDiagonal, upperDiagonal);
    }
    else
        score = globalAlignment(alignment, scoringScheme, alignConfig);

    std::string s1Name = "s1";
    std::string s2Name = "s2";

    return new ScoredAlignment(alignment, s1Name, s2Name, s1.length(), s2.length(),
                               0, startTime, 0, true, true, scoringScheme);
}

