import * as React from 'react';
import { useEffect, useState } from 'react';
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
import { green } from '@mui/material/colors';

const config = require('../config.json');




export default function CustomPage() {

    const [position, setPosition] = useState(null);
    const [cardState, setCardState] = useState(1);
    const [fortyState, setFortyState] = useState(4.5);
    const [heightState, setHeightState] = useState(6-2);
    const [weightState, setWeightState] = useState(200);
    const [broadState, setBroadState] = useState(100);
    const [coneState, setConeState] = useState(4.15);
    const [verticalState, setVerticalState] = useState(35);
    const [shuttleState, setShuttleState] = useState(6.9);
    const [benchState, setBenchState] = useState(30);


    const [passAttState, setPassAttState] = useState(500);
    const [pctState, setPctState] = useState(50);
    const [passYardsState, setPassYardsState] = useState(2000);
    const [passTouchdownsState, setPassTouchdownsState] = useState(50);
    const [intState, setIntState] = useState(20);
    const [ratingState, setRatingState] = useState(100);
    const [rushYardsState, setRushYardsState] = useState(500);
    const [rushTdState, setRushTdState] = useState(10);


    const [rbYardsState, setRbYardsState] = useState(2000);
    const [rbAttState, setRbAttState] = useState(500);
    const [rbAvgState, setRbAvgState] = useState(4.5);
    const [rbTdState, setRbTdState] = useState(20);


    const [recState, setRecState] = useState(500);
    const [recYardsState, setrecYardsState] = useState(2000);
    const [recTdState, setRecTdState] = useState(20);
    const [predictState, setPredictState] = useState(false);
    const [prediction, setPrediction] = useState(null);

    useEffect( () => {
      if(cardState == 6){
      if(position == 'QB'){
        // fetch(`http://${config.server_host}:${config.server_port}/prediction?position=${position}&forty=${fortyState}&height=${heightState}&weight=${weightState}&broad=${broadState}&cone=${coneState}&vertical=${verticalState}&shuttle=${shuttleState}&bench=${benchState}&attempts=${passAttState}&percent=${pctState}&pass_yards=${passYardsState}&pass_td=${passTouchdownsState}&interceptions=${intState}&qbr=${ratingState}&r_yds=${rushYardsState}&r_td=${rushTdState}`)
        fetch(`https://${config.server_host}/prediction?position=${position}&forty=${fortyState}&height=${heightState}&weight=${weightState}&broad=${broadState}&cone=${coneState}&vertical=${verticalState}&shuttle=${shuttleState}&bench=${benchState}&attempts=${passAttState}&percent=${pctState}&pass_yards=${passYardsState}&pass_td=${passTouchdownsState}&interceptions=${intState}&qbr=${ratingState}&r_yds=${rushYardsState}&r_td=${rushTdState}`)
        .then(res => res.json())
        .then(resJson=> {
          setPrediction(resJson.prediction);
        })
      } else if(position == 'RB'){
        // fetch(`http://${config.server_host}:${config.server_port}/prediction?position=${position}&forty=${fortyState}&height=${heightState}&weight=${weightState}&broad=${broadState}&cone=${coneState}&vertical=${verticalState}&shuttle=${shuttleState}&bench=${benchState}&r_att=${rbAttState}&r_avg=${rbAvgState}&r_yds=${rbYardsState}&r_td=${rbTdState}`)
        fetch(`https://${config.server_host}/prediction?position=${position}&forty=${fortyState}&height=${heightState}&weight=${weightState}&broad=${broadState}&cone=${coneState}&vertical=${verticalState}&shuttle=${shuttleState}&bench=${benchState}&r_att=${rbAttState}&r_avg=${rbAvgState}&r_yds=${rbYardsState}&r_td=${rbTdState}`)
        .then(res => res.json())
        .then(resJson=> {
          setPrediction(resJson.prediction);
        })
      } else {
        // fetch(`http://${config.server_host}:${config.server_port}/prediction?position=${position}&forty=${fortyState}&height=${heightState}&weight=${weightState}&broad=${broadState}&cone=${coneState}&vertical=${verticalState}&shuttle=${shuttleState}&bench=${benchState}&rec=${recState}&rec_avg=${recTdState}&rec_yds=${recYardsState}&rec_td=${recTdState}`)     
        const route = `https://${config.server_host}/prediction?position=${position}&forty=${fortyState}&height=${heightState}&weight=${weightState}&broad=${broadState}&cone=${coneState}&vertical=${verticalState}&shuttle=${shuttleState}&bench=${benchState}&rec=${recState}&rec_avg=${recTdState}&rec_yds=${recYardsState}&rec_td=${recTdState}`;
        fetch(`https://${config.server_host}/prediction?position=${position}&forty=${fortyState}&height=${heightState}&weight=${weightState}&broad=${broadState}&cone=${coneState}&vertical=${verticalState}&shuttle=${shuttleState}&bench=${benchState}&rec=${recState}&rec_avg=${recTdState}&rec_yds=${recYardsState}&rec_td=${recTdState}`)     
        .then(res => res.json())
        .then(resJson=> {
          console.log(resJson, " prediction returned");
          setPrediction(resJson.prediction);
        }) 
      }
    }}, [cardState]
    );



    const setNextPosition = () => {
      if(position == 'QB'){
        setCardState(3);
      } else if(position == 'RB'){
        setCardState(4);
      } else {
        setCardState(5);
      }
    }



    if(cardState == 1){
        return(
            // <p>test test please work</p>
            <Box  sx={{
                display: 'flex',
                justifyContent: 'center', 
                mt: 10 // top margin 
            }}>
            <Card sx={{ maxWidth: 1900 }}> 
            <CardContent>
                <FormControl fullWidth sx={{ minWidth: 200, mt: 10, mb:10 }}>
                <InputLabel id="demo-simple-select-label">Position</InputLabel>
                <Select
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={position}
                    label="Position"
                    onChange={ (change) => {setPosition(change.target.value); setCardState(2)}}
                >
                    <MenuItem value={'QB'}>QB</MenuItem>
                    <MenuItem value={'RB'}>RB</MenuItem>
                    <MenuItem value={'WR'}>WR</MenuItem>
                    <MenuItem value={'TE'}>TE</MenuItem>
                </Select>
                </FormControl>
            </CardContent>
            </Card>
            </Box>
        );
    } else if(cardState == 2){
        return(
          <Box  sx={{
            display: 'flex',
            justifyContent: 'center', 
            mt: 10, 
            gap: 2
        }}>
        <Card sx={{ maxWidth: 1900 }}> 
        <CardContent>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>

          <TextField
            label="40 Yard Dash"
            id="dash-1"
            defaultValue={fortyState}
            onChange={(val)=> {setFortyState(val.target.value)}}
            size="small"
          />
          <TextField
            label="Height"
            id="height-1"
            defaultValue={heightState}
            onChange={(val)=> {setHeightState(val.target.value)}}

            size="small"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Weight"
            id="weight"
            defaultValue={weightState}
            onChange={(val)=> {setWeightState(val.target.value)}}
            size="small"
          />
          <TextField
            label="Shuttle"
            id="Shuttle"
            defaultValue={shuttleState}
            onChange={(val)=> {setShuttleState(val.target.value)}}
            size="small"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Cone"
            id="Cone"
            defaultValue={coneState}
            onChange={(val)=> {setConeState(val.target.value)}}
            size="small"
          />
          <TextField
            label="Broad Jump"
            id="Broad"
            defaultValue={broadState}
            onChange={(val)=> {setBroadState(val.target.value)}}
            size="small"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Bench"
            id="Bench"
            defaultValue={benchState}
            onChange={(val)=> {setBenchState(val.target.value)}}
            size="small"
          />
          <TextField
            label="Vertical"
            id="Vertical"
            defaultValue={verticalState}
            onChange={(val)=> {setVerticalState(val.target.value)}}
            size="small"
          />
        </Box>

        <Box sx={{ justifyContent: 'center',  display: 'flex', gap: 2, mb: 2 }}>
        <Button variant="contained" onClick={setNextPosition}>Next</Button>
        </Box>

        </CardContent>
        </Card>
    </Box>
        );
    } else if(cardState == 3){
      return(
        <Box  sx={{
          display: 'flex',
          justifyContent: 'center', 
          mt: 10, 
          gap: 2
      }}>
      <Card sx={{ maxWidth: 1900 }}> 
      <CardContent>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>

        <TextField
          label="Pass Attempts"
          id="dash-1"
          defaultValue={passAttState}
          onChange={(val)=> {setPassAttState(val.target.value)}}
          size="small"
        />
        <TextField
          label="Completion Pct"
          id="height-1"
          defaultValue={pctState}
          onChange={(val)=> {setPctState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Passing Yards"
          id="weight"
          defaultValue={passYardsState}
          onChange={(val)=> {setPassYardsState(val.target.value)}}
          size="small"
        />
        <TextField
          label="Touchdowns"
          id="Shuttle"
          defaultValue={passTouchdownsState}
          onChange={(val)=> {setPassTouchdownsState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Interceptions"
          id="Cone"
          defaultValue={intState}
          onChange={(val)=> {setIntState(val.target.value)}}
          size="small"
        />
        <TextField
          label="Passer Rating"
          id="Broad"
          defaultValue={ratingState}
          onChange={(val)=> {setRatingState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Rushing Yards"
          id="Bench"
          defaultValue={rushYardsState}
          onChange={(val)=> {setRushYardsState(val.target.value)}}
          size="small"
        />
        <TextField
          label="Rushing Touchdowns"
          id="Vertical"
          defaultValue={rushTdState}
          onChange={(val)=> {setRushTdState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ justifyContent: 'center',  display: 'flex', gap: 2, mb: 2 }}>
      <Button variant="contained" onClick={() => {setNextPosition(); setPredictState(true); setCardState(6);}}>Predict</Button>
      </Box>

      </CardContent>
      </Card>
  </Box>
      );
    }

    else if(cardState == 4){
      return(
        <Box  sx={{
          display: 'flex',
          justifyContent: 'center', 
          mt: 10, 
          gap: 2
      }}>
      <Card sx={{ maxWidth: 1900 }}> 
      <CardContent>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>

        <TextField
          label="Rushing Attempts"
          id="dash-1"
          defaultValue={rbAttState}
          onChange={(val)=> {setRbAttState(val.target.value)}}
          size="small"
        />
        <TextField
          label="Rushing Yards"
          id="height-1"
          defaultValue={rbYardsState}
          onChange={(val)=> {setRbYardsState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
      <TextField
          label="Average"
          id="height-1"
          defaultValue={rbAvgState}
          onChange={(val)=> {setRbAvgState(val.target.value)}}
          size="small"
        />
        <TextField
          label="Touchdowns"
          id="weight"
          defaultValue={rbTdState}
          onChange={(val)=> {setRbTdState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ justifyContent: 'center',  display: 'flex', gap: 2, mb: 2 }}>
      <Button variant="contained" onClick={() => {setNextPosition(); setPredictState(true); setCardState(6);}}>Predict</Button>
      </Box>

      </CardContent>
      </Card>
  </Box>
      );
    }
    else if(cardState == 5){
      return(
        <Box  sx={{
          display: 'flex',
          justifyContent: 'center', 
          mt: 10, 
          gap: 2
      }}>
      <Card sx={{ maxWidth: 1900 }}> 
      <CardContent>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>

        <TextField
          label="Receptions"
          id="receptions"
          defaultValue={recState}
          onChange={(val)=> {setRecState(val.target.value)}}
          size="small"
        />
        <TextField
          label="Receiving Yards"
          id="rec"
          defaultValue={recYardsState}
          onChange={(val)=> {setrecYardsState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Touchdowns"
          id="weight"
          defaultValue={recTdState}
          onChange={(val)=> {setRecTdState(val.target.value)}}
          size="small"
        />
      </Box>

      <Box sx={{ justifyContent: 'center',  display: 'flex', gap: 2, mb: 2 }}>
      <Button variant="contained" onClick={() => {setNextPosition(); setPredictState(true); setCardState(6);}}>Predict</Button>
      </Box>

      </CardContent>
      </Card>
  </Box>
      );
    } else if(cardState == 6){
      return(
        <Box  sx={{
          display: 'flex',
          justifyContent: 'center', 
          mt: 10, 
          gap: 2, 
      }}>
      <Card sx={{ maxWidth: 1900, bgcolor: 'green'}}> 
      <CardContent>
      <Box sx={{ display: 'flex', gap: 2, mb: 2}}>
        <Typography variant='h1' color='white'>
            {prediction}
        </Typography>
      </Box>
      </CardContent>
      </Card>
  </Box>
  );
    }

}