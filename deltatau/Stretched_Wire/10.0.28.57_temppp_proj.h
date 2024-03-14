
#ifndef _PP_PROJ_H_
#define _PP_PROJ_H_
//***********************************************************************************
// C header for accessing PMAC Global, CSGlobal, Ptr vars
// _PPScriptMode_ for Pmac Script like access global & csglobal
// global Mypvar - access with "Mypvar"
// global Myparray(32) - access with "Myparray(i)"
// csglobal Myqvar - access with "Myqvar(i)" where "i" is Coord #
// csglobal Myqarray(16) - access with "Myqvar(i,j)" where "j" is index
// _EnumMode_ for Pmac enum data type checking on Set & Get global functions
// Example
// global Mypvar
// csglobal Myqvar
// "SetGlobalVar(Myqvar, data)" will give a compile error because its a csglobal var.
// "SetCSGlobalVar(Mypvar, data)" will give a compile error because its a global var.
//************************************************************************************

#ifdef _PPScriptMode_
enum globalP {_globalP_=-1};
enum globalParray {_globalParray_=-1};
enum csglobalQ {_csglobalQ_=-1};
enum csglobalQarray {_csglobalQarray_=-1};

enum ptrM {_ptrM_=-1};
enum ptrMarray {_ptrMarray_=-1};
#define	CompAddDist	pshm->P[8192]
#define	ComparePos	pshm->P[8193]
#define	distance	pshm->P[8194]
#define	acce	pshm->P[8195]
#define	n_scans	pshm->P[8196]
#define	Motor1Homed	pshm->P[8197]
#define	Motor1HomeSpeed	pshm->P[8198]
#define	Motor2Homed	pshm->P[8199]
#define	Motor2HomeSpeed	pshm->P[8200]
#define	Motor3Homed	pshm->P[8201]
#define	Motor3HomeSpeed	pshm->P[8202]
#define	Motor4Homed	pshm->P[8203]
#define	Motor4HomeSpeed	pshm->P[8204]
#define	Motor5Homed	pshm->P[8205]
#define	Motor5HomeSpeed	pshm->P[8206]
#define	Motor6Homed	pshm->P[8207]
#define	Motor6HomeSpeed	pshm->P[8208]
#define	SyncError_fI_horizontal	pshm->P[8209]
#define	SyncError_sI_horizontal	pshm->P[8210]
#define	SyncError_fI_vertical	pshm->P[8211]
#define	SyncError_sI_vertical	pshm->P[8212]
#define	VelError_h	pshm->P[8213]
#define	VelError_v	pshm->P[8214]
#define	MovError	pshm->P[8215]
#define	EncPos	pshm->P[8216]
#define	start_pos	pshm->P[8217]
#define	end_pos	pshm->P[8218]
#define	steps	pshm->P[8219]
#define	bl_comp	pshm->P[8220]
#define	wait	pshm->P[8221]
#define	r_jerk	pshm->P[8222]
#define	r_a	pshm->P[8223]
#define	r_s	pshm->P[8224]
#define	motion_flag	pshm->P[8225]
#define	bl_flag	pshm->P[8226]
#define	measure_flag	pshm->P[8227]
#define	Ch1MaxAdc	pshm->P[8228]
#define	Ch1RmsPeakCur	pshm->P[8229]
#define	Ch1RmsContCur	pshm->P[8230]
#define	Ch1TimeAtPeak	pshm->P[8231]
#define	Ch2MaxAdc	pshm->P[8232]
#define	Ch2RmsPeakCur	pshm->P[8233]
#define	Ch2RmsContCur	pshm->P[8234]
#define	Ch2TimeAtPeak	pshm->P[8235]
#define	Ch3MaxAdc	pshm->P[8236]
#define	Ch3RmsPeakCur	pshm->P[8237]
#define	Ch3RmsContCur	pshm->P[8238]
#define	Ch3TimeAtPeak	pshm->P[8239]
#define	Ch4MaxAdc	pshm->P[8240]
#define	Ch4RmsPeakCur	pshm->P[8241]
#define	Ch4RmsContCur	pshm->P[8242]
#define	Ch4TimeAtPeak	pshm->P[8243]
#ifndef _PP_PROJ_HDR_
  void SetEnumGlobalVar(enum globalP var, double data)
  {
    pshm->P[var] = data;
  }

  double GetEnumGlobalVar(enum globalP var)
  {
    return pshm->P[var];
  }

  void SetEnumGlobalArrayVar(enum globalParray var, unsigned index, double data)
  {
    pshm->P[(var + index)%MAX_P] = data;
  }

  double GetEnumGlobalArrayVar(enum globalParray var, unsigned index)
  {
    return pshm->P[(var + index)%MAX_P];
  }

  void SetEnumCSGlobalVar(enum csglobalQ var, unsigned cs, double data)
  {
    pshm->Coord[cs % MAX_COORDS].Q[var] = data;
  }

  double GetEnumCSGlobalVar(enum csglobalQ var, unsigned cs)
  {
    return pshm->Coord[cs % MAX_COORDS].Q[var];
  }

  void SetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs, double data)
  {
    pshm->Coord[cs % MAX_COORDS].Q[(var + index)%MAX_Q] = data;
  }

  double GetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs)
  {
    return pshm->Coord[cs % MAX_COORDS].Q[(var + index)%MAX_Q];
  }

  void SetEnumPtrVar(enum ptrM var, double data)
  {
    im_write(pshm->Mdef + var, data, &pshm->Ldata);
  }

  double GetEnumPtrVar(enum ptrM var)
  {
    return im_read(pshm->Mdef + var, &pshm->Ldata);
  }

  void SetEnumPtrArrayVar(enum ptrMarray var, unsigned index, double data)
  {
    im_write(pshm->Mdef + ((var + index)%MAX_M), data, &pshm->Ldata);
  }

  double GetEnumPtrArrayVar(enum ptrMarray var, unsigned index)
  {
    return im_read(pshm->Mdef + ((var + index)%MAX_M), &pshm->Ldata);
  }

  #define SetGlobalVar(i, x)              SetEnumGlobalVar(i, x)
  #define SetGlobalArrayVar(i, j, x)      SetEnumGlobalArrayVar(i, j, x)
  #define GetGlobalVar(i)                 GetEnumGlobalVar(i)
  #define GetGlobalArrayVar(i, j)         GetEnumGlobalArrayVar(i, j)

  #define SetCSGlobalVar(i, j, x)         SetEnumCSGlobalVar(i, j, x)
  #define SetCSGlobalArrayVar(i, j, k, x) SetEnumCSGlobalArrayVar(i, j, k, x)
  #define GetCSGlobalVar(i, j)            GetEnumCSGlobalVar(i, j)
  #define GetCSGlobalArrayVar(i, j, k)    GetEnumCSGlobalArrayVar(i, j, k)

  #define SetPtrVar(i, x)                 SetEnumPtrVar(i, x)
  #define SetPtrArrayVar(i, j, x)         SetEnumPtrArrayVar(i, j, x)
  #define GetPtrVar(i)                    GetEnumPtrVar(i)
  #define GetPtrArrayVar(i, j)            GetEnumPtrArrayVar(i, j)

#else

  void SetEnumGlobalVar(enum globalP var, double data);
  double GetEnumGlobalVar(enum globalP var);
  void SetEnumGlobalArrayVar(enum globalParray var, unsigned index, double data);
  double GetEnumGlobalArrayVar(enum globalParray var, unsigned index);
  void SetEnumCSGlobalVar(enum csglobalQ var, unsigned cs, double data);
  double GetEnumCSGlobalVar(enum csglobalQ var, unsigned cs);
  void SetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs, double data);
  double GetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs);
  void SetEnumPtrVar(enum ptrM var, double data);
  double GetEnumPtrVar(enum ptrM var);
  void SetEnumPtrArrayVar(enum ptrMarray var, unsigned index, double data);
  double GetEnumPtrArrayVar(enum ptrMarray var, unsigned index);

  #define SetGlobalVar(i, x)              SetEnumGlobalVar(i, x)
  #define SetGlobalArrayVar(i, j, x)      SetEnumGlobalArrayVar(i, j, x)
  #define GetGlobalVar(i)                 GetEnumGlobalVar(i)
  #define GetGlobalArrayVar(i, j)         GetEnumGlobalArrayVar(i, j)

  #define SetCSGlobalVar(i, j, x)         SetEnumCSGlobalVar(i, j, x)
  #define SetCSGlobalArrayVar(i, j, k, x) SetEnumCSGlobalArrayVar(i, j, k, x)
  #define GetCSGlobalVar(i, j)            GetEnumCSGlobalVar(i, j)
  #define GetCSGlobalArrayVar(i, j, k)    GetEnumCSGlobalArrayVar(i, j, k)

  #define SetPtrVar(i, x)                 SetEnumPtrVar(i, x)
  #define SetPtrArrayVar(i, j, x)         SetEnumPtrArrayVar(i, j, x)
  #define GetPtrVar(i)                    GetEnumPtrVar(i)
  #define GetPtrArrayVar(i, j)            GetEnumPtrArrayVar(i, j)

#endif
// end of #ifdef _PPScriptMode_
#else
#ifdef _EnumMode_
enum globalP {_globalP_=-1
,CompAddDist=8192
,ComparePos=8193
,distance=8194
,acce=8195
,n_scans=8196
,Motor1Homed=8197
,Motor1HomeSpeed=8198
,Motor2Homed=8199
,Motor2HomeSpeed=8200
,Motor3Homed=8201
,Motor3HomeSpeed=8202
,Motor4Homed=8203
,Motor4HomeSpeed=8204
,Motor5Homed=8205
,Motor5HomeSpeed=8206
,Motor6Homed=8207
,Motor6HomeSpeed=8208
,SyncError_fI_horizontal=8209
,SyncError_sI_horizontal=8210
,SyncError_fI_vertical=8211
,SyncError_sI_vertical=8212
,VelError_h=8213
,VelError_v=8214
,MovError=8215
,EncPos=8216
,start_pos=8217
,end_pos=8218
,steps=8219
,bl_comp=8220
,wait=8221
,r_jerk=8222
,r_a=8223
,r_s=8224
,motion_flag=8225
,bl_flag=8226
,measure_flag=8227
,Ch1MaxAdc=8228
,Ch1RmsPeakCur=8229
,Ch1RmsContCur=8230
,Ch1TimeAtPeak=8231
,Ch2MaxAdc=8232
,Ch2RmsPeakCur=8233
,Ch2RmsContCur=8234
,Ch2TimeAtPeak=8235
,Ch3MaxAdc=8236
,Ch3RmsPeakCur=8237
,Ch3RmsContCur=8238
,Ch3TimeAtPeak=8239
,Ch4MaxAdc=8240
,Ch4RmsPeakCur=8241
,Ch4RmsContCur=8242
,Ch4TimeAtPeak=8243};
enum globalParray {_globalParray_=-1};
enum csglobalQ {_csglobalQ_=-1};
enum csglobalQarray {_csglobalQarray_=-1};
enum ptrM {_ptrM_=-1};
enum ptrMarray {_ptrMarray_=-1};
#ifndef _PP_PROJ_HDR_
  void SetEnumGlobalVar(enum globalP var, double data)
  {
    pshm->P[var] = data;
  }

  double GetEnumGlobalVar(enum globalP var)
  {
    return pshm->P[var];
  }

  void SetEnumGlobalArrayVar(enum globalParray var, unsigned index, double data)
  {
    pshm->P[(var + index)%MAX_P] = data;
  }

  double GetEnumGlobalArrayVar(enum globalParray var, unsigned index)
  {
    return pshm->P[(var + index)%MAX_P];
  }

  void SetEnumCSGlobalVar(enum csglobalQ var, unsigned cs, double data)
  {
    pshm->Coord[cs % MAX_COORDS].Q[var] = data;
  }

  double GetEnumCSGlobalVar(enum csglobalQ var, unsigned cs)
  {
    return pshm->Coord[cs % MAX_COORDS].Q[var];
  }

  void SetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs, double data)
  {
    pshm->Coord[cs % MAX_COORDS].Q[(var + index)%MAX_Q] = data;
  }

  double GetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs)
  {
    return pshm->Coord[cs % MAX_COORDS].Q[(var + index)%MAX_Q];
  }

  void SetEnumPtrVar(enum ptrM var, double data)
  {
    im_write(pshm->Mdef + var, data, &pshm->Ldata);
  }

  double GetEnumPtrVar(enum ptrM var)
  {
    return im_read(pshm->Mdef + var, &pshm->Ldata);
  }

  void SetEnumPtrArrayVar(enum ptrMarray var, unsigned index, double data)
  {
    im_write(pshm->Mdef + ((var + index)%MAX_M), data, &pshm->Ldata);
  }

  double GetEnumPtrArrayVar(enum ptrMarray var, unsigned index)
  {
    return im_read(pshm->Mdef + ((var + index)%MAX_M), &pshm->Ldata);
  }

  #define SetGlobalVar(i, x)              SetEnumGlobalVar(i, x)
  #define SetGlobalArrayVar(i, j, x)      SetEnumGlobalArrayVar(i, j, x)
  #define GetGlobalVar(i)                 GetEnumGlobalVar(i)
  #define GetGlobalArrayVar(i, j)         GetEnumGlobalArrayVar(i, j)

  #define SetCSGlobalVar(i, j, x)         SetEnumCSGlobalVar(i, j, x)
  #define SetCSGlobalArrayVar(i, j, k, x) SetEnumCSGlobalArrayVar(i, j, k, x)
  #define GetCSGlobalVar(i, j)            GetEnumCSGlobalVar(i, j)
  #define GetCSGlobalArrayVar(i, j, k)    GetEnumCSGlobalArrayVar(i, j, k)

  #define SetPtrVar(i, x)                 SetEnumPtrVar(i, x)
  #define SetPtrArrayVar(i, j, x)         SetEnumPtrArrayVar(i, j, x)
  #define GetPtrVar(i)                    GetEnumPtrVar(i)
  #define GetPtrArrayVar(i, j)            GetEnumPtrArrayVar(i, j)

#else

  void SetEnumGlobalVar(enum globalP var, double data);
  double GetEnumGlobalVar(enum globalP var);
  void SetEnumGlobalArrayVar(enum globalParray var, unsigned index, double data);
  double GetEnumGlobalArrayVar(enum globalParray var, unsigned index);
  void SetEnumCSGlobalVar(enum csglobalQ var, unsigned cs, double data);
  double GetEnumCSGlobalVar(enum csglobalQ var, unsigned cs);
  void SetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs, double data);
  double GetEnumCSGlobalArrayVar(enum csglobalQarray var, unsigned index, unsigned cs);
  void SetEnumPtrVar(enum ptrM var, double data);
  double GetEnumPtrVar(enum ptrM var);
  void SetEnumPtrArrayVar(enum ptrMarray var, unsigned index, double data);
  double GetEnumPtrArrayVar(enum ptrMarray var, unsigned index);

  #define SetGlobalVar(i, x)              SetEnumGlobalVar(i, x)
  #define SetGlobalArrayVar(i, j, x)      SetEnumGlobalArrayVar(i, j, x)
  #define GetGlobalVar(i)                 GetEnumGlobalVar(i)
  #define GetGlobalArrayVar(i, j)         GetEnumGlobalArrayVar(i, j)

  #define SetCSGlobalVar(i, j, x)         SetEnumCSGlobalVar(i, j, x)
  #define SetCSGlobalArrayVar(i, j, k, x) SetEnumCSGlobalArrayVar(i, j, k, x)
  #define GetCSGlobalVar(i, j)            GetEnumCSGlobalVar(i, j)
  #define GetCSGlobalArrayVar(i, j, k)    GetEnumCSGlobalArrayVar(i, j, k)

  #define SetPtrVar(i, x)                 SetEnumPtrVar(i, x)
  #define SetPtrArrayVar(i, j, x)         SetEnumPtrArrayVar(i, j, x)
  #define GetPtrVar(i)                    GetEnumPtrVar(i)
  #define GetPtrArrayVar(i, j)            GetEnumPtrArrayVar(i, j)

#endif
// end of #ifdef _EnumMode_
#else
// ***** Standard default mode *****
#define CompAddDist 8192
#define ComparePos 8193
#define distance 8194
#define acce 8195
#define n_scans 8196
#define Motor1Homed 8197
#define Motor1HomeSpeed 8198
#define Motor2Homed 8199
#define Motor2HomeSpeed 8200
#define Motor3Homed 8201
#define Motor3HomeSpeed 8202
#define Motor4Homed 8203
#define Motor4HomeSpeed 8204
#define Motor5Homed 8205
#define Motor5HomeSpeed 8206
#define Motor6Homed 8207
#define Motor6HomeSpeed 8208
#define SyncError_fI_horizontal 8209
#define SyncError_sI_horizontal 8210
#define SyncError_fI_vertical 8211
#define SyncError_sI_vertical 8212
#define VelError_h 8213
#define VelError_v 8214
#define MovError 8215
#define EncPos 8216
#define start_pos 8217
#define end_pos 8218
#define steps 8219
#define bl_comp 8220
#define wait 8221
#define r_jerk 8222
#define r_a 8223
#define r_s 8224
#define motion_flag 8225
#define bl_flag 8226
#define measure_flag 8227
#define Ch1MaxAdc 8228
#define Ch1RmsPeakCur 8229
#define Ch1RmsContCur 8230
#define Ch1TimeAtPeak 8231
#define Ch2MaxAdc 8232
#define Ch2RmsPeakCur 8233
#define Ch2RmsContCur 8234
#define Ch2TimeAtPeak 8235
#define Ch3MaxAdc 8236
#define Ch3RmsPeakCur 8237
#define Ch3RmsContCur 8238
#define Ch3TimeAtPeak 8239
#define Ch4MaxAdc 8240
#define Ch4RmsPeakCur 8241
#define Ch4RmsContCur 8242
#define Ch4TimeAtPeak 8243
#endif
#endif
#endif //_PP_PROJ_H_
