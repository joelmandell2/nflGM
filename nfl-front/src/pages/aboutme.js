import * as React from 'react';
import {
    Box,
    Button,
    Card,
    CardContent,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    Slider
  } from '@mui/material';

const config = require('../config.json');


export default function AboutMe(){
    return (
        <Box sx={{display:'flex',
                justifyContent:'center', 
                mt: 10}}> 
            <Card sx={{ mr: 10, ml: 10, mb: 10}}>
                <CardContent>
                <p1>This model was created utilizing combine and collegiate statistics scraped from sports reference. Data was scraped from the years
                2007-2025, and each trait was normalized and used as a feature on a scale of the min/max values. 
                Each player in the training set was classified based upon their NFL stats using a rating system based on position.
                I chose to only analyze offensive skill positions, since they were the most likely to have stats available to analyze
                their performance. Players were then sorted based on their predicted NFL success, with green being a pro bowl caliber player, 
                light blue representing a starter, dark blue a backup, and black a bust. Players can also be sorted by attribute by clicking
                on the desired sorted category.
                <br/>
                <br/>
                Quarterback's NFL success was predicted using a Random Forest model producing an overall 51% precision, 58% recall, and a 53% accuracy 
                in predicting All Pro level prospects. The quarterback classification model was quite successful in predicting the quarterbacks 
                who would not find success in the NFL. In the 10 years analyzed, only two players predicted to be busts ended up making a pro bowl, 
                and one of which did not work out at the combine, which likely resulted in an inaccurate prediction. 
                Additionally, the model was highly successful in predicting quarterbacks that would go on to reach pro bowl levels of success in the NFL
                with correct predictions including Josh Allen, Joe Burrow, Lamar Jackson, Jalen Hurts, Dak Prescott, and  Trevor Lawrence.
                <br/>
                <br/>
                Wide receivers were also predicted using a Random Forest model with an overall accuracy of 80%, with 80% recall and a 76% accuracy for All Pro
                along with 80% bust accuracy. Wide receivers as a group had a much larger sample size than quarterback, simply due to there being a much 
                larger number of wide receivers entering the draft, which likely accounts for this increase in accuracy. One feature to notice is that 
                even when a model slightly misses on an All Pro prospect, it still comes very close, with these misses usually being predicted to be starters,
                so drawing from the prospects in the All Pro and Starter pool, this model is very accurate. For example, in the 2021 class, none of the 
                26 players predicted to be busts turned out to be a starter in the NFL, while players predicted to be All Pro players or starters include
                Nico Collins, Amon Ra St Brown, and Ja'Marr Chase, all players who had over 1,000 receiving yards in the past year alone.
                <br/>
                <br/>
                Tight end was a slightly more difficult position to classify, because a tight end's value is not as quantifiable as a wide receiver's, due 
                to tight ends being much more invovled in blocking. However, using the tight end's receiving statistics alone and a multiclass perceptron model
                I was able to achieve an overall 92% prediction accuracy for tight ends, however it was only 29% accurate in finding all pro players. This accuracy
                is largely driven by a 97% accuracy in picking which prospects would turn out to be busts. 
                <br/>
                <br/> 
                Finally, running back received a 57% overall accuracy, with 63% All Pro. The running back rating system I used was a bit too generous and 
                overrated many players to be much better than their actual performance, however it was still largely accurate in selecting players that wound up 
                being succesful in the NFL. 
                <br/>
                <br/>
                Obviously, the model won't be as accurate at predicting outcomes as something like an object detector due to the unpredictability
                of NFL draft prospects, relatively small sample sizes of only a few hundred players, and an increasingly large number of prospects opting out of participating in combine workouts. However, for certain positions, 
                such as wide receiver, the model is very successful at predicting outcomes, much better 
                than the average NFL fan would be. Is it good enough to replace an NFL GM? Probably not, but hey, maybe if an NFL team doesn't want to spend 10 million dollars a year to spend on a GM and scouting department, they could use this model
                instead and use that money to buy a left tackle. <br/>
                </p1>
                </CardContent>
        
            </Card>
        </Box>
        

        
    );
}