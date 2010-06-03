<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
	<head>
		<title>Compute X-ray Absorption</title>
		<link rel="shortcut icon" href="../images/favicon.ico"> 
		<link href="../stylesheet.css" rel="stylesheet" type="text/css">
	</head>

<body> 
    <table width="100%" border="0" cellpadding="0" cellspacing="3">
<!-------TOP HEADER-----------------------------------------------TOP HEADER--->
        <tr> 
            <td colspan="2">
            <table width="100%"  border="0" cellspacing="0" cellpadding="0">
                <tr class="headerBkgd" valign="middle">
                    <td class="leftbanner"><a href="http://www.anl.gov/"><img src="../images/argonne_header_logo.jpg" alt="Argonne National Laboratory" width="227" height="100" border="0"></a></td>
                        <td><p>
                            <a href="http://www.aps.anl.gov" class="sectionTitle">Advanced Photon Source<br></a>
                            <img src="../images/spacer.gif" width="1" height="5" border="0" alt=""><br>
			    <a href="http://11bm.xor.aps.anl.gov" class="whiteText">Compute X-ray Absorption<br></a>
                        </p></td>
                    <td class="rightbanner"><a href="http://www.energy.gov/"><img src="../images/header_doe.gif" alt="US Dept. of Energy" border="0"></a></td>
                </tr>
            </table>
            </td>
        </tr>
<tr valign="top">
    <td>
    <table width="100%" border="0" cellpadding="5" cellspacing="0" bgcolor=#F1EEE8>
        <tr> 
            <td class="mainbody">
  
<a name="MainContent"></a>
   <blockquote><font face="arial, helvetica, sans-serif">

<?php
$mode = strip_tags($_GET['mode']);
if ($mode == "") {
#===============================================================================
# initial call, put up the web form
#===============================================================================
?>

<!-----MAIN BODY----------------------------------------------------MAIN BODY-->

<h2>Compute X-ray Absorption</h2>
    <I>Absorption computation utility routine by Robert B. Von Dreele, Matthew R. Suchomel and Brian H. Toby.</I><P>
   <FORM METHOD="GET" ACTION="<?php echo $_SERVER['PHP_SELF']; ?>">
    <INPUT TYPE="hidden" NAME="mode" value="calc">

<B>Select X-ray Wavelength or Energy:</B>
   <BR>
   <SELECT NAME="spectrumtype">
   <OPTION VALUE="Wavelength" SELECTED> Wavelength (&Aring;)
   <OPTION VALUE="Energy"> Energy (keV)
   </SELECT>
   <input name="spectrum" size=20 value="0.41">
<BR>
<BR>

<B>Chemical Formula:</B><br>
    <div style="font-size:small;"><i>enter using element chemical symbol & optional fractional number, e.g. YBa2Cu3O6.5. (Proper capitalization is required).</i></div>
<input name="formula" size=50 value="">
<BR>
<BR>

<B>Sample Radius:</B><br>
<input name="radius" size=5 value="0.35"><span style="font-size:small;"><i>  capillary radius in mm</i></span>
<BR>
<BR>
 
<B>Sample Density or Packing Fraction</B>
<div style="font-size:small;"><i>enter either measured sample density or estimated packing fraction</i></div>
   <SELECT NAME="densitytype">
   <OPTION VALUE="RHO"> Sample Density (g/cc)
   <OPTION SELECTED> Packed Fraction (0.0 - 1.0)
   </SELECT>
   <input name="density" size=10 value="0.6">
<BR>
<BR>
 
<INPUT TYPE="submit" VALUE="Compute" NAME="submit">
<INPUT TYPE="reset" VALUE="Clear Form">
</form>
<!---- Last Updated------------------------------------------ Last Updated----->
                            <p align="center" class="mod">
                                    <script type="text/javascript">
                                        <!--
                                        da = new Date(document.lastModified)
                                        db = da.toGMTString()
                                        dc = db.split(" ")
                                        if ( eval( dc[3] ) < 1970 ) dc[3] = eval( dc[3] ) +100
                                        db = dc[1] + " " + dc[2] + " " + dc[3]
                                        document.write ( "Last Updated: " + db )
                                        // -->
                                    </script>
                            </p>
<?php
 } else {
#===============================================================================
# 2nd call perform the computation
#===============================================================================
  print "<h2>X-ray Absorption Computation</h2>";
  $now = date("ymdhis", time());
  $imageroot = "Abs" . $now . getmypid() . ".png";
  $imageloc="/tmp/absorbplots/";
  $imagefile=$imageloc . $imageroot;
  if (file_exists($imagefile)) {
    unlink($imagefile);
  } else {
    if (! file_exists($imageloc)) {
      mkdir($imageloc);
    }
  }
  $type = strip_tags($_GET['spectrumtype']);
  $value = strip_tags($_GET['spectrum']);
  $formula = strip_tags($_GET['formula']);
  $radius = strip_tags($_GET['radius']);
  
  if (strstr($type, "Wavelength")) {
    $iwave = 1;
  } else {
    $iwave = 0;
  }
  $densitytype = strip_tags($_GET['densitytype']);
  $density = strip_tags($_GET['density']);
  if (strstr($densitytype, "RHO")) {
    $irho = 0;
  } else {
    $irho = 1;
  }
  
  $descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("file", "/tmp/absorbplots/error-output.txt", "w") // stderr is a file to write
			  );
  $process = proc_open('python /home/joule/WEB11BM/www/absorb/runweb.py', $descriptorspec, $pipes);
  if (is_resource($process)) {
    $fp = $pipes[0];
    fwrite($fp, $formula . "\n");
    fwrite($fp, $radius . "\n");
    fwrite($fp, $imagefile . "\n");
    fwrite($fp, $iwave . "\n");
    fwrite($fp, $value . "\n");
    fwrite($fp, $irho . "\n");
    fwrite($fp, $density . "\n");
    fclose($pipes[0]);
    while(!feof($pipes[1])) { 
      print fgets($pipes[1]);
    }
    if (file_exists($imagefile)) {
      print '<P><img src="plotimg/' . $imageroot . '">';
      print "<BR><I>".
	"The plot above shows the absorption for each input element and for " . 
	"the specified composition as a function of x-ray wavelength/energy." .
	" The blue dotted line indicates a muR value of 1. In a capillary " . 
	"(Debye-Scherrer) geometry, it is ideal when muR is 1 or below, as ".
	"sample absorption is minimal and no correction is usually needed. " .
	"The red dotted line indicates a muR value of 5. For muR >= 5, ".
	" measurements are generally not possible in a capillary ".
	"geometry, as there will be very severe levels of absorption and ".
	"corrections are inaccurate.</I>";
    } else {
      print "<H3>An error occurred running the script, please check your input</H3>";
    }
  } else {
    print "no process created<BR>";
  }
 }
?>
                        </td> 
                    </tr> 
                </table>
            
                <img src="../images/spacer.gif" width="800" height="1" border="0" alt=""> 
            </td>
        </tr>
        
<!---------Footer------------------------------------------------------Footer-->  
        <tr valign="top"> 
            <td colspan="2"><table width="100%" border="0" cellspacing="0" cellpadding="0"> 
                
                <tr> 
                    <td colspan="2" align="left" style="border-top:1px solid #666;font-size:9px;color:#bbb;"> &nbsp; </td>            
                </tr>
                
                <tr>
                    <td>&nbsp;</td>
                        <td align="center" style="width:100%;">
                            <a href="http://www.sc.doe.gov/" class="footlink">U.S. Department of Energy Office of Science</a>&nbsp;<div class="foot">|</div>&nbsp;
                            <a href="http://www.sc.doe.gov/bes/" class="footlink">Office of Basic Energy Sciences</a>&nbsp;<div class="foot">|</div>&nbsp;
                            <a href="http://www.uchicagoargonnellc.org/" class="footlink">UChicago Argonne LLC</a>
                        </td>
                    <td>&nbsp;</td>
                </tr>
                
                <tr>
                    <td align="center">&nbsp;</td>
                        <td align="center" style="width:100%;">
                            <a href="http://www.anl.gov/notice.html" class="footlink">Privacy &amp; Security Notice</a>&nbsp;<div class="foot">|</div>&nbsp;
                            <a href="http://www.aps.anl.gov/Users/Contacts/" class="footlink">Contact Us</a>&nbsp;<div class="foot">|</div>&nbsp;
                            <a href="http://www.aps.anl.gov/site_map.html" class="footlink">Site Map</a>
                        </td>
                    <td >&nbsp;</td>
                </tr>
            </table></td> 
        </tr> 

    </table>



</body>

</html>
