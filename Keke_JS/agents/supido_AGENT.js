// BABA IS Y'ALL SOLVER - BLANK TEMPLATE
// Version 1.0
// Code by Milk 


//get imports (NODEJS)
var simjs = require('../js/simulation')					//access the game states and simulation

let possActions = ["space", "right", "up", "left", "down"];

var count = 0;

// NEXT ITERATION STEP FOR SOLVING
function iterSolve(init_state){
	// PERFORM ITERATIVE CALCULATIONS HERE //

	if(count<1){
		//
		console.log(init_state);
		if(count==3)
		{
			console.log(simjs.parseMap(simjs.showState(init_state)));
		}
		//return a sequence of actions or empty list
		count++;
		return ['right'];
	}
	return [''];
}

function init()
{
	count = 0;
}


// VISIBLE FUNCTION FOR OTHER JS FILES (NODEJS)
module.exports = {
	step : function(init_state){return iterSolve(init_state)},		// iterative step function (returns solution as list of steps from poss_actions or empty list)
	init : function(init_state){init()},							// initializing function here
	best_sol : function(){return [];}				//returns closest solution in case of timeout
}


