import { useEffect, useState } from 'react';
import { Box, Button, ButtonGroup, Modal } from '@mui/material';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import { NavLink } from 'react-router-dom';

const config = require('../config.json');



export default function PlayerCard({playerName, year, pos, handleClose}){

    // actual data being graphed
    const [playerData, setPlayerData] = useState({});
    // used to simplify query on which files to search
    const [draftYear, setDraftYear] = useState({year});
    const [position, setPosition] = useState({pos});
    // controls which chart shows up on screen
    const [barRadar, setBarRadar] = useState(true);
    

    useEffect( () => {
        // fetch(`http://${config.server_host}:${config.server_port}/player_page?p_name=${playerName}&draft_year=${year}&position=${pos}`)

        fetch(`https://${config.server_host}/player_page?p_name=${playerName}&draft_year=${year}&position=${pos}`)
        .then(res => res.json())
        .then(resJson => {
            setPlayerData(resJson);
            setPosition(pos);
            setDraftYear(year);
            console.log(resJson, ' json returned from server');
        });
        // need to fetch from year and player name
    }, [playerName]);


    const handleGraphData = () => {
        setBarRadar(!barRadar);
    };

    // fix what chart data returns based on position
    const player_data = [
                {name: 'Completion pct', value: playerData.PCT},
                {name: 'Rating', value: playerData.Rating},
                {name: 'Touchdowns', value: playerData.Touchdowns},
            ];

    const rb_data = [
        {name: 'Attempts', value: playerData.ATT},
        {name: 'Yards', value: playerData.Yards},
        {name: 'Touchdowns', value: playerData.Touchdowns}
    ];

    const wr_data = [{name: 'Receptions', value: playerData.Receptions},
    {name: 'Yards', value: playerData.Yards},
    {name: 'Touchdowns', value: playerData.Touchdowns}];


    function data_parse(){
        if(position == 'QB'){
            return player_data;
        } else if (position == 'RB'){
            return rb_data;
        } else if (position == 'WR' || position == 'TE') {
            return wr_data;
        }else {
            return wr_data;
        }
    }

    // modal controls whether popup is rendered 
    return (
        <Modal
        open={true}
        onClose={handleClose}
        style={{display:'flex', justifyContent: 'center', alignItems: 'center'}}
        >
        <Box
        p={3}
        style={{ background: 'white', borderRadius: '16px', border: '2px solid #000', width: 600 }}
        >
        <h1>{playerData.name}</h1>
        <ButtonGroup>
            <Button disabled={barRadar} onClick={handleGraphData}>Bar</Button>
            <Button disabled={!barRadar} onClick={handleGraphData}>Radar</Button>
        </ButtonGroup>
        <div style={{ margin: 20 }}>
        {
            barRadar ? (
                <ResponsiveContainer height={250}>
                    <BarChart
                    data={data_parse()}
                    layout='horizontal'
                    margin={{left: 40}}
                    >
                    <XAxis type='category' dataKey='name' domain={[0, 200]} />
                    <YAxis type='number' dataKey='value' />
                    <Bar dataKey='value' stroke='#8884d8' fill='#8884d8' />
                    </BarChart>
                </ResponsiveContainer>
            ) : (
                <ResponsiveContainer height={250}>
                    <RadarChart outerRadius={90} width={730} height={250} data={data_parse()}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="name" />
                    <PolarRadiusAxis angle={30} domain={[0, 200]} />
                    <Radar name={playerData.name} dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    </RadarChart>
                </ResponsiveContainer>
            )
        }
        </div>
        <Button onClick={handleClose} style={{ left: '50%', transform: 'translateX(-50%)' }} >
          Close
        </Button>
        </Box>
        </Modal>
    );
}