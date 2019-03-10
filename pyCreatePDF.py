import os
import datetime
from xhtml2pdf import pisa
import webbrowser
now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
outputFilename=os.getcwd()+'\Reports\Raman_PLS'+str(now)+'.pdf'
def createHTML():
	html = '<body><h1>Raman PLS Regression from '+str(now)+'</h1><h1>Obs VS. Predicted </h1><img src="'+os.getcwd()+'\OvsP.png" alt="Smiley face"><p>'\
	'<img src="'+os.getcwd()+'\OvsP2.png" alt="Smiley face"><p>'\
	'<h1>Number of Components</h1><img src="'+os.getcwd()+'\oofComp.png" alt="Smiley face"><p>'\
    '<h1>Spectra</h1><img src="'+os.getcwd()+'\spectraSGSNV.png" alt="Smiley face"><p>'
	return html
sourceHtml=createHTML()
def convertHtmlToPdf(sourceHtml,outputFilename):
    resultFile = open(outputFilename, "w+b")
    pisaStatus = pisa.CreatePDF(
            sourceHtml,                
            dest=resultFile)           
    resultFile.close()
    os.startfile(outputFilename)
    #webbrowser.open(outputFilename)
#if __name__ == "__main__":
#    pisa.showLogging()
#    convertHtmlToPdf(sourceHtml, outputFilename)
