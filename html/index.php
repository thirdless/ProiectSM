<?php

    $file_path = "/var/www/settings.json";

    //error message for API pages
    function send_error($message){
        http_response_code(403);
        echo $message;
        die();
    }

    //function for settings changes
    function change_settings($param, $value){
        global $file_path;
        
        //object which stores the desired settings
        $content = (object)[];

        //loading the already existent settings to be overwritten by the new changes
        if(file_exists($file_path))
            $content = json_decode(file_get_contents($file_path));

        //changing if the value exists, and if it doesn't, the property gets deleted
        if($value == "")
            unset($content->$param);
        else
            $content->$param = $value;

        //writing the values back into the file
        file_put_contents($file_path, json_encode($content));

        //alternative and inefficient - instant execution of the routine function to modify the shown values on the screen
        // exec("sudo python3 /home/pi/watch/routine.py 2>&1", $output);
        // print_r($output);

        //creating a new empty file to let the main process know that there were changes to the configuration file
        file_put_contents("/var/www/UPDATE_DATA", "");

        //exiting php script
        die();
    }

    $type = null;

    //checking if the typed location exists and return the API page status
    function check_weather($loc){
        @file_get_contents("http://wttr.in/" . urlencode($loc) . "?format=%t", false, stream_context_create(["http" => ["ignore_errors" => true]]));

        //checking http header and returning the page status
        if(!empty($http_response_header) && count($http_response_header) > 1){
            $parts = explode(" ", $http_response_header[0]);
            return (int)$parts[1];
        }
        else{
            //returning 404 error if the API cannot be reached
            return 404;
        }
    }

    //choosing the setting type
    //syncronization setting, just storing the boolean option
    if(isset($_POST["sincronizare"]))
        $type = "sincronizare";
    //location setting, checking if the requested location exists
    else if(isset($_POST["locatie"])){
        $check = check_weather($_POST["locatie"]);

        if($check == 200)
            $type = "locatie";
        else
            send_error("Eroare: locatia selectata nu exista");
    }
    //custom time setting, checking if the requested time is correct and also storing a system timestamp - chosen timestamp pair, for difference calculus
    else if(isset($_POST["ora"]) && strpos($_POST["ora"], ";") !== false){
        $parts = explode(";", $_POST["ora"]);
        $parts[0] = $parts[0] == "" ? 0 : $parts[0];
        $parts[1] = $parts[1] == "" ? 0 : $parts[1];
        $custom = strtotime(date("j F Y") . " " . $parts[0] . ":" . $parts[1]);

        if($custom === false || (int)$parts[0] < 0 || (int)$parts[1] < 0)
            send_error("Eroare: timpul selectat este unul incorect");

        change_settings("ora", time() . ";" . $custom);
    }

    //changing the settings by type, one at a time
    if($type != null)
        change_settings($type, $_POST[$type]);

    //getting the existing settings to be shown on the webpage
    if(file_exists($file_path)){
        //reading the file
        $settings = json_decode(file_get_contents($file_path));

        //getting the simple settings
        if(isset($settings->sincronizare))
            $sync = $settings->sincronizare;
        if(isset($settings->locatie))
            $location = $settings->locatie;
        
        //calculating the custom time, the sum of the current system timestamp and the difference between the two values stored as a pair
        if(isset($settings->ora) && strpos($settings->ora, ";") !== false){
            $diff = time() - (int)(explode(";", $settings->ora)[0]);
            $custom = (int)(explode(";", $settings->ora)[1]) + $diff;
            $custom = explode(";", date("G;i", $custom));
            $hours = $custom[0];
            $minutes = $custom[1];
        }
    }

    //checking the time sync checkbox
    $sincronizare = isset($sync) && $sync == "true";

?>
<!DOCTYPE html>
<html>
    <head>
        <title>Office clock - SM Project</title>
        <meta charset="utf-8"/>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat"/>
        <link rel="stylesheet" href="index.css"/>
    </head>
    <body>
        <div class="main">
            <h1>Office clock - SM Project</h1>
            <div>
                <span>Sync clock with the internet:</span>
                <label class="ceas_internet">
                    <input type="checkbox" name="ceas_internet" <?= $sincronizare ? "checked" : "" ?>>
                    <div class="check"></div>
                </label>
            </div>
            <div class="set <?= $sincronizare ? "disabled" : "" ?>">
                <span>Set the time:</span>
                <input type="number" name="ceas_ora" placeholder="H" value="<?= isset($hours) ? htmlspecialchars($hours) : "" ?>">
                <input type="number" name="ceas_minut" placeholder="M" value="<?= isset($minutes) ? htmlspecialchars($minutes) : "" ?>">
            </div>
            <div>
                <span>Weather location:</span>
                <input type="text" name="ceas_locatie" placeholder="Current location by IP" value="<?= isset($location) ? htmlspecialchars($location) : "" ?>">
            </div>
        </div>
        <script src="index.js"></script>
    </body>
</html>
