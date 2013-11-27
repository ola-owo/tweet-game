var myMarquee, myMarqueeDiv; 
var foo = 600; 
var bar = 0; 
var mTog, mDur;

function loadMarquee() 
{  myMarqueeDiv = document.getElementById('innerMarquee'); 
   if(myMarqueeDiv==null) {  return false; } 
   if(myMarqueeDiv.innerHTML==null) { return false }
   mDur = (myMarqueeDiv.innerHTML.length * 8 );  // approx length for text in px.
   if(mDur < 600) mDur = 600;
   myMarquee = setInterval('scrollMarquee()',1); 
} 

function scrollMarquee() 
{ 
   if(foo > 0)  {  foo-=5;  myMarqueeDiv.style.marginLeft = foo+'px';  } 
   else 
   {  
       bar +=1; 
       if( bar < mDur ) { myMarqueeDiv.style.marginLeft = '-'+(bar)+'px'; } 
       else { myMarqueeDiv.style.marginLeft = '600'; bar = 0; foo = 600; } 
   } 
   return true;
} 

function toggleMarquee() 
{
   if(!mTog) { clearInterval(myMarquee);  mTog=1; }
   else { loadMarquee(); mTog=0; } 
   return true;
}

window.onload = function(e) { loadMarquee(); } 
