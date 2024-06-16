import military_exercise as mi
import sys

def main():
   file_in = "data/testcase1.in"
   file_out = "data/testcase1.out"
   m = mi.Map(file_in)
 
   max_frame = 15000
   with open(file_out,'w') as f:
      original_stdout = sys.stdout
      sys.stdout = f
      for i in range(max_frame):
         # if i == 403:
         #    i=403
         for plane in m.Planes :
            m.plane_control(plane)
            if (m.lost_plane == m.num_of_plane) or (m.lost_redbase == m.num_of_red) :
               return 
         print("OK")
      sys.stdout = original_stdout
         



if __name__ == "__main__":
   main();