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
      if(position == 'QB'){
        fetch(`http://${config.server_host}:${config.server_port}/prediction?p_name=${playerName}&draft_year=${year}&position=${pos}`)
      } else if(position == 'RB'){
        fetch(`http://${config.server_host}:${config.server_port}/prediction?p_name=${playerName}&draft_year=${year}&position=${pos}`)

      } else {
        fetch(`http://${config.server_host}:${config.server_port}/prediction?p_name=${playerName}&draft_year=${year}&position=${pos}`)
      }
    }, [predictState]
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
            onChange={(val)=> {setFortyState(val)}}
            size="small"
          />
          <TextField
            label="Height"
            id="height-1"
            defaultValue={heightState}
            onChange={(val)=> {setHeightState(val)}}

            size="small"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Weight"
            id="weight"
            defaultValue={weightState}
            onChange={(val)=> {setWeightState(val)}}
            size="small"
          />
          <TextField
            label="Shuttle"
            id="Shuttle"
            defaultValue={shuttleState}
            onChange={(val)=> {setShuttleState(val)}}
            size="small"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Cone"
            id="Cone"
            defaultValue={coneState}
            onChange={(val)=> {setConeState(val)}}
            size="small"
          />
          <TextField
            label="Broad Jump"
            id="Broad"
            defaultValue={broadState}
            onChange={(val)=> {setBroadState(val)}}
            size="small"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Bench"
            id="Bench"
            defaultValue={benchState}
            onChange={(val)=> {setBenchState(val)}}
            size="small"
          />
          <TextField
            label="Vertical"
            id="Vertical"
            defaultValue={verticalState}
            onChange={(val)=> {setVerticalState(val)}}
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
          onChange={(val)=> {setPassAttState(val)}}
          size="small"
        />
        <TextField
          label="Completion Pct"
          id="height-1"
          defaultValue={pctState}
          onChange={(val)=> {setPctState(val)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Passing Yards"
          id="weight"
          defaultValue={passYardsState}
          onChange={(val)=> {setPassYardsState(val)}}
          size="small"
        />
        <TextField
          label="Touchdowns"
          id="Shuttle"
          defaultValue={passTouchdownsState}
          onChange={(val)=> {setPassTouchdownsState(val)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Interceptions"
          id="Cone"
          defaultValue={intState}
          onChange={(val)=> {setIntState(val)}}
          size="small"
        />
        <TextField
          label="Passer Rating"
          id="Broad"
          defaultValue={ratingState}
          onChange={(val)=> {setRatingState(val)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Rushing Yards"
          id="Bench"
          defaultValue={rushYardsState}
          onChange={(val)=> {setRushYardsState(val)}}
          size="small"
        />
        <TextField
          label="Rushing Touchdowns"
          id="Vertical"
          defaultValue={rushTdState}
          onChange={(val)=> {setRushTdState(val)}}
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
          onChange={(val)=> {setRbAttState(val)}}
          size="small"
        />
        <TextField
          label="Rushing Yards"
          id="height-1"
          defaultValue={rbYardsState}
          onChange={(val)=> {setRbYardsState(val)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
      <TextField
          label="Average"
          id="height-1"
          defaultValue={rbAvgState}
          onChange={(val)=> {setRbAvgState(val)}}
          size="small"
        />
        <TextField
          label="Touchdowns"
          id="weight"
          defaultValue={rbTdState}
          onChange={(val)=> {setRbTdState(val)}}
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
          onChange={(val)=> {setRecState(val)}}
          size="small"
        />
        <TextField
          label="Receiving Yards"
          id="rec"
          defaultValue={recYardsState}
          onChange={(val)=> {setrecYardsState(val)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Touchdowns"
          id="weight"
          defaultValue={recTdState}
          onChange={(val)=> {setRecTdState(val)}}
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
          gap: 2
      }}>
      <Card sx={{ maxWidth: 1900 }}> 
      <CardContent>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>

        <TextField
          label="Receptions"
          id="receptions"
          defaultValue={recState}
          onChange={(val)=> {setRecState(val)}}
          size="small"
        />
        <TextField
          label="Receiving Yards"
          id="rec"
          defaultValue={recYardsState}
          onChange={(val)=> {setrecYardsState(val)}}
          size="small"
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="Touchdowns"
          id="weight"
          defaultValue={recTdState}
          onChange={(val)=> {setRecTdState(val)}}
          size="small"
        />
      </Box>

      <Box sx={{ justifyContent: 'center',  display: 'flex', gap: 2, mb: 2 }}>
      </Box>
      </CardContent>
      </Card>
  </Box>
  );
    }

}