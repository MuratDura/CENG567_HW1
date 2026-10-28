|decision_index|action|old_pos|new_pos|world_time|hp|energy|camp_kits|enemy_flags|has_treasure|trap_active|reward|terminated|truncated|event|enemies_killed|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|1|MOVE_RIGHT|(0, 0)|(0, 1)|1|3|19|2|[1, 1]|False|False|-0.2|False|False|move|0|
|2|MOVE_RIGHT|(0, 1)|(0, 2)|2|3|18|2|[1, 1]|False|False|-0.2|False|False|move|0|
|3|MOVE_DOWN|(0, 2)|(1, 2)|3|3|17|2|[1, 1]|False|True|-0.2|False|False|move|0|
|4|MOVE_RIGHT|(1, 2)|(1, 3)|4|3|16|2|[1, 1]|False|False|-0.2|False|False|move|0|
|5|MOVE_DOWN|(1, 3)|(2, 3)|5|2|13|2|[1, 1]|False|False|-0.2|False|False|move;enemy_0_hit|0|
|6|ATTACK_RIGHT|(2, 3)|(2, 3)|6|2|10|2|[0, 1]|False|True|9.8|False|False|attack;enemy_0_killed|1|
|7|MOVE_RIGHT|(2, 3)|(2, 4)|7|2|9|2|[0, 1]|False|False|-0.2|False|False|move|0|
|8|MOVE_DOWN|(2, 4)|(3, 4)|8|2|8|2|[0, 1]|False|False|-0.2|False|False|move|0|
|9|MOVE_DOWN|(3, 4)|(4, 4)|9|2|7|2|[0, 1]|False|True|-0.2|False|False|move|0|
|10|MOVE_DOWN|(4, 4)|(5, 4)|10|2|6|2|[0, 1]|False|False|-0.2|False|False|move|0|
|11|MOVE_RIGHT|(5, 4)|(5, 5)|11|2|5|2|[0, 1]|False|False|-0.2|False|False|move|0|
|12|MOVE_RIGHT|(5, 5)|(5, 6)|12|2|4|2|[0, 1]|False|True|-0.2|False|False|move|0|
|13|MOVE_DOWN|(5, 6)|(6, 6)|13|2|3|2|[0, 1]|True|False|-0.2|False|False|move;treasure_collected|0|
|14|CAMP|(6, 6)|(6, 6)|18|3|20|1|[0, 1]|True|True|-1.0|False|False|camp_started;camp_completed|0|
|15|MOVE_UP|(6, 6)|(5, 6)|19|3|19|1|[0, 1]|True|False|-0.2|False|False|move|0|
|16|MOVE_LEFT|(5, 6)|(5, 5)|20|3|18|1|[0, 1]|True|False|-0.2|False|False|move|0|
|17|MOVE_LEFT|(5, 5)|(5, 4)|21|3|17|1|[0, 1]|True|True|-0.2|False|False|move|0|
|18|MOVE_UP|(5, 4)|(4, 4)|22|3|16|1|[0, 1]|True|False|-0.2|False|False|move|0|
|19|MOVE_UP|(4, 4)|(3, 4)|23|3|15|1|[0, 1]|True|False|-0.2|False|False|move|0|
|20|MOVE_UP|(3, 4)|(2, 4)|24|3|14|1|[0, 1]|True|True|-0.2|False|False|move|0|
|21|MOVE_LEFT|(2, 4)|(2, 3)|25|3|13|1|[0, 1]|True|False|-0.2|False|False|move|0|
|22|MOVE_UP|(2, 3)|(1, 3)|26|3|12|1|[0, 1]|True|False|-0.2|False|False|move|0|
|23|MOVE_LEFT|(1, 3)|(1, 2)|27|3|11|1|[0, 1]|True|True|-0.2|False|False|move|0|
|24|MOVE_UP|(1, 2)|(0, 2)|28|3|10|1|[0, 1]|True|False|-0.2|False|False|move|0|
|25|MOVE_LEFT|(0, 2)|(0, 1)|29|3|9|1|[0, 1]|True|False|-0.2|False|False|move|0|
|26|MOVE_LEFT|(0, 1)|(0, 0)|30|3|8|1|[0, 1]|True|True|99.8|True|False|move;win|0|