// import { useEffect, useState } from 'react';
// import { Box, Button, ButtonGroup, Modal } from '@mui/material';
// import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
// import { NavLink } from 'react-router-dom';

// import { formatDuration } from '../helpers/formatter';
// const config = require('../config.json');



// export default function PlayerCard({playerName, year, pos, handleClose}){

//     // actual data being graphed
//     const [playerData, setPlayerData] = useState({});
//     // used to simplify query on which files to search
//     const [draftYear, setDraftYear] = useState({year});
//     const [position, setPosition] = useState({pos});
//     // controls which chart shows up on screen
//     const [barRadar, setBarRadar] = useState(true);
    

//     useEffect( () => {
//         fetch(`http://${config.server_host}:${config.server_port}/player/?p_name=${playerName}?draft_year=${year}?position=${pos}`)
//         .then(res => res.json())
//         .then(resJson => {
//             setPlayerData(resJson);
//         });
//         // need to fetch from year and player name
//     }, [playerName]);


//     const handleGraphData = () => {
//         setBarRadar(!barRadar);
//     };

//     // fix what chart data returns based on position
//     const chartData = () => {
//         if(position == 'QB'){
//             return [
//                 {name: 'Name', value: playerData.name},
//                 {name: 'Attempts', value: playerData.att},
//                 {name: 'Yards', value: playerData.yards},
//                 {name: 'Touchdowns', value: playerData.touchdowns},
//             ];
//         } else if(position == 'RB'){
//             return [
//                 {name: 'Name', value: playerData.name},
//                 {name: 'Rushes', value: playerData.rushes},
//                 {name: 'Yards', value: playerData.yards},
//                 {name: 'Touchdowns', value: playerData.touchdowns},
//             ];
//         } else {
//             return [
//                 {name: 'Name', value: playerData.name},
//                 {name: 'Receptions', value: playerData.rec},
//                 {name: 'Yards', value: playerData.yards},
//                 {name: 'Touchdowns', value: playerData.touchdowns},
//             ]
//         }
//     }



//     // modal controls whether popup is rendered 
//     return (
//         <Modal
//         open={true}
//         onClose={handleClose}
//         style={{display:'flex', justifyContent: 'center', alignItems: 'center'}}
//         >
//         <Box
//         p={3}
//         style={{ background: 'white', borderRadius: '16px', border: '2px solid #000', width: 600 }}
//         >
//         <h1>{playerData.name}</h1>
//         <ButtonGroup>
//             <Button disabled={barRadar} onClick={handleGraphData}>Bar</Button>
//             <Button disabled={!barRadar} onClick={handleGraphData}>Radar</Button>
//         </ButtonGroup>
//         <div style={{ margin: 20 }}>
//         {
//             barRadar ? (
//                 <ResponsiveContainer height={250}>
//                     <BarChart
//                     data={chartData}
//                     layout='vertical'
//                     margin={{left: 40}}
//                     >
//                     <XAxis type='number' domain={[0, 1]} />
//                     <YAxis type='category' dataKey='name' />
//                     <Bar dataKey='value' stroke='#8884d8' fill='#8884d8' />
//                     </BarChart>
//                 </ResponsiveContainer>
//             ) : (
//                 <ResponsiveContainer height={250}>
//                     <PolarGrid />
//                     <PolarAngleAxis dataKey="name" />
//                     <PolarRadiusAxis angle={30} domain={[0, 1]} />
//                     <Radar name={songData.title} dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
//                 </ResponsiveContainer>
//             )
//         }
//         </div>
//         <Button onClick={handleClose} style={{ left: '50%', transform: 'translateX(-50%)' }} >
//           Close
//         </Button>
//         </Box>
//         </Modal>
//     );
// }