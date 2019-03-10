import spc
f = spc.File('/home/pyadmin/sambashare/Raman/spc/2015-09-2302-04-24_Spectrum.spc')  # read file
#x-y(20)  # format string
f.data_txt()  # output data
f.write_file('output.txt')  # write data to file
#f.plot()  # plot data